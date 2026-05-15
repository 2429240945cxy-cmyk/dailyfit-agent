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
    small.textContent = meta;
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
}

function renderList(targetId, rows, formatter) {
  const target = $(targetId);
  target.innerHTML = "";
  if (!rows || rows.length === 0) {
    const li = document.createElement("li");
    li.textContent = "None";
    target.appendChild(li);
    return;
  }
  for (const row of rows) {
    const li = document.createElement("li");
    li.textContent = formatter(row);
    target.appendChild(li);
  }
}

function renderResult(data) {
  $("guardianBox").textContent = data.guardian?.verdict || "-";
  $("traceBox").textContent = data.trace_id || "-";
  $("tokensBox").textContent = `${data.usage?.input_tokens || 0}/${data.usage?.output_tokens || 0}`;
  $("costBox").textContent = `$${Number(data.usage?.cost_usd || 0).toFixed(6)}`;
  $("cacheBox").textContent = String(Boolean(data.usage?.cache_hit));
  $("traceInput").value = data.trace_id || "";

  renderList("memoryList", data.memory_hits || [], (hit) => `${hit.summary} (${hit.score})`);
  renderList("sourceList", data.source_attribution || [], (source) => {
    const fallback = source.fallback_used ? ` fallback=${source.fallback_reason}` : "";
    return `${source.name}: ${source.source}${fallback}`;
  });
  $("toolBox").textContent = pretty(data.tool_results || []);
}

async function send(messageOverride) {
  const message = (messageOverride || $("message").value).trim();
  if (!message) return;

  $("sendBtn").disabled = true;
  appendMessage("user", message);
  const pending = appendMessage("assistant", "Thinking...", "calling agent");

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
    pending.querySelector("p").textContent = data.response || "";
    pending.querySelector("small").textContent =
      `trace ${data.trace_id} · guardian ${data.guardian?.verdict || "-"} · ` +
      `tokens ${(data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0)} · ` +
      `$${Number(data.usage?.cost_usd || 0).toFixed(6)}`;
    renderResult(data);
    $("message").value = "";
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
  $("benchmarkBox").textContent = pretty(data.results || []);
}

for (const btn of document.querySelectorAll("[data-demo]")) {
  btn.addEventListener("click", () => {
    $("message").value = btn.dataset.demo;
    $("message").focus();
  });
}

$("chatForm").addEventListener("submit", (event) => {
  event.preventDefault();
  send();
});

$("message").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    send();
  }
});

$("loadAuditBtn").addEventListener("click", loadAudit);

loadHealth().catch((err) => {
  $("healthBadge").textContent = err.message;
});
loadLogs().catch(() => {});
loadBenchmarks().catch(() => {});
