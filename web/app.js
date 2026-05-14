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

async function loadHealth() {
  const health = await getJson("/health");
  $("modeBadge").textContent = health.public_mode || health.mode;
  $("providerBadge").textContent = `${health.provider}/${health.model}`;
  $("healthBadge").textContent = health.status;
}

function renderResult(data) {
  $("responseBox").textContent = data.response || "";
  $("guardianBox").textContent = data.guardian?.verdict || "-";
  $("traceBox").textContent = data.trace_id || "-";
  $("tokensBox").textContent = `${data.usage?.input_tokens || 0}/${data.usage?.output_tokens || 0}`;
  $("costBox").textContent = `$${Number(data.usage?.cost_usd || 0).toFixed(6)}`;
  $("cacheBox").textContent = String(Boolean(data.usage?.cache_hit));
  $("traceInput").value = data.trace_id || "";

  $("memoryList").innerHTML = "";
  for (const hit of data.memory_hits || []) {
    const li = document.createElement("li");
    li.textContent = `${hit.summary} (${hit.score})`;
    $("memoryList").appendChild(li);
  }

  $("sourceList").innerHTML = "";
  for (const source of data.source_attribution || []) {
    const li = document.createElement("li");
    li.textContent = `${source.name}: ${source.source}${source.fallback_used ? ` fallback=${source.fallback_reason}` : ""}`;
    $("sourceList").appendChild(li);
  }

  $("toolBox").textContent = pretty(data.tool_results || []);
}

async function send() {
  $("sendBtn").disabled = true;
  try {
    const data = await getJson("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: $("userId").value,
        session_id: $("sessionId").value,
        message: $("message").value,
      }),
    });
    renderResult(data);
    await loadLogs();
  } catch (err) {
    $("responseBox").textContent = `Error: ${err.message}`;
  } finally {
    $("sendBtn").disabled = false;
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
    btn.className = "ghost";
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
  });
}

$("sendBtn").addEventListener("click", send);
$("loadAuditBtn").addEventListener("click", loadAudit);

loadHealth().catch((err) => {
  $("healthBadge").textContent = err.message;
});
loadLogs().catch(() => {});
loadBenchmarks().catch(() => {});
