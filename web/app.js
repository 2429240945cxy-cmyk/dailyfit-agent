const $ = (id) => document.getElementById(id);

async function getJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${text}`);
  }
  return res.json();
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function formatAssistantText(text) {
  return (text || "").trim() || "No response returned.";
}

function setMeta(container, meta) {
  container.innerHTML = "";
  for (const part of meta.split("·").map((item) => item.trim()).filter(Boolean)) {
    const span = document.createElement("span");
    span.textContent = part;
    container.appendChild(span);
  }
}

function appendMessage(role, text, meta = "") {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "DF";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const body = document.createElement("p");
  body.textContent = text;
  bubble.appendChild(body);

  if (meta) {
    const small = document.createElement("small");
    setMeta(small, meta);
    bubble.appendChild(small);
  }

  article.appendChild(avatar);
  article.appendChild(bubble);
  $("conversation").appendChild(article);
  $("conversation").scrollTop = $("conversation").scrollHeight;
  return article;
}

async function loadHealth() {
  const health = await getJson("/health");
  $("modeBadge").textContent = health.public_mode || health.mode;
  $("providerBadge").textContent = `${health.provider}/${health.model}`;
  $("healthBadge").textContent = health.status;
  $("modeText").textContent = health.public_mode || health.mode;
}

function renderList(targetId, rows, formatter) {
  const target = $(targetId);
  target.innerHTML = "";
  if (!rows || rows.length === 0) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "No items yet";
    target.appendChild(li);
    return;
  }
  for (const row of rows) {
    const li = document.createElement("li");
    li.className = "list-card";
    li.textContent = formatter(row);
    target.appendChild(li);
  }
}

function renderResult(data) {
  $("guardianBox").textContent = `Guardian ${data.guardian?.verdict || "-"}`;
  $("traceBox").textContent = data.trace_id || "-";
  const totalTokens = (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0);
  $("tokensBox").textContent = `${totalTokens} tokens`;
  $("costBox").textContent = `$${Number(data.usage?.cost_usd || 0).toFixed(6)}`;
  $("cacheBox").textContent = `cache ${String(Boolean(data.usage?.cache_hit))}`;
  $("sessionScore").textContent = data.mode || "Ready";
  $("traceInput").value = data.trace_id || "";

  renderList("memoryList", data.memory_hits || [], (hit) => `${hit.summary} (${hit.score})`);
  renderList("sourceList", data.source_attribution || [], (source) => {
    const fallback = source.fallback_used ? ` fallback=${source.fallback_reason}` : "";
    return `${source.name} · ${source.source}${fallback}`;
  });
  $("toolBox").textContent = pretty(data.tool_results || []);
}

async function send(messageOverride) {
  const message = (messageOverride || $("message").value).trim();
  if (!message) return;

  $("sendBtn").disabled = true;
  appendMessage("user", message);
  const pending = appendMessage("assistant", "DailyFit is thinking", "calling agent");
  pending.classList.add("pending");

  try {
    const data = await getJson("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: $("userId").value,
        session_id: $("sessionId").value,
        message,
      }),
    });
    pending.classList.remove("pending");
    pending.querySelector("p").textContent = formatAssistantText(data.response);
    setMeta(
      pending.querySelector("small"),
      `trace ${data.trace_id} · ${data.mode} · guardian ${data.guardian?.verdict || "-"} · ` +
      `tokens ${(data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0)} · cache ${Boolean(data.usage?.cache_hit)} · ` +
      `$${Number(data.usage?.cost_usd || 0).toFixed(6)}`
    );
    renderResult(data);
    $("message").value = "";
    autosizeMessage();
    await loadLogs();
  } catch (err) {
    pending.querySelector("p").textContent = `Error: ${err.message}`;
    pending.classList.add("error");
  } finally {
    $("sendBtn").disabled = false;
    $("message").focus();
  }
}

async function loadAudit() {
  const traceId = $("traceInput").value.trim();
  if (!traceId) return;
  const audit = await getJson(`/logs/${encodeURIComponent(traceId)}`);
  $("auditBox").textContent = pretty(audit);
}

async function loadLogs() {
  const data = await getJson("/logs");
  $("logsList").innerHTML = "";
  for (const log of data.logs || []) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "link-button";
    btn.type = "button";
    btn.textContent = log.trace_id;
    btn.onclick = async () => {
      $("traceInput").value = log.trace_id;
      await loadAudit();
    };
    li.appendChild(btn);
    li.append(` ${log.intent || ""} ${log.created_at || ""}`);
    $("logsList").appendChild(li);
  }
}

async function loadBenchmarks() {
  const data = await getJson("/benchmarks/latest");
  const rows = (data.results || []).slice(0, 4).map((item) => ({
    benchmark: item.benchmark,
    mode: item.mode,
    samples: item.sample_count,
    metrics: item.metrics,
  }));
  $("benchmarkBox").textContent = pretty(rows);
}

for (const btn of document.querySelectorAll("[data-demo]")) {
  btn.addEventListener("click", () => {
    $("message").value = btn.dataset.demo;
    autosizeMessage();
    $("message").focus();
  });
}

$("chatForm").addEventListener("submit", (event) => {
  event.preventDefault();
  send();
});

$("message").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    send();
  }
});

function autosizeMessage() {
  const box = $("message");
  box.style.height = "auto";
  box.style.height = `${Math.min(box.scrollHeight, 180)}px`;
}

$("message").addEventListener("input", autosizeMessage);
$("loadAuditBtn").addEventListener("click", loadAudit);

renderList("memoryList", [], (row) => row);
renderList("sourceList", [], (row) => row);
$("toolBox").textContent = "[]";
$("auditBox").textContent = "{}";
$("benchmarkBox").textContent = "Loading benchmarks...";

loadHealth().catch((err) => {
  $("healthBadge").textContent = err.message;
});
loadLogs().catch(() => {});
loadBenchmarks().catch(() => {});
