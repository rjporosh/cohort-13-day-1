"""
web_chat.py — Browser e ChatGPT-er moto chat UI for the Task Server.

Run (same folder as server_task_porosh.py):
    mcp-env/bin/python web_chat.py

Then open:  http://127.0.0.1:5050
"""

from flask import Flask, jsonify, request

from server_task_porosh import _answer_question, load_database

app = Flask(__name__)


# ============================================================
# BROWSER PAGE (HTML + CSS + JS — single file)
# ============================================================

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Task Assistant</title>
<style>
  :root { --bg:#f4f4f5; --card:#ffffff; --accent:#0f766e; --text:#1f2937; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         background:var(--bg); color:var(--text); height:100vh; display:flex; flex-direction:column; }
  header { background:#111827; color:#fff; padding:14px 20px; display:flex;
           justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; }
  header h1 { font-size:18px; margin:0; }
  #stats { font-size:13px; opacity:.9; }
  #refresh { background:#374151; color:#fff; border:none; padding:6px 12px;
             border-radius:8px; cursor:pointer; font-size:13px; }
  #chat { flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column;
          gap:10px; max-width:820px; width:100%; margin:0 auto; }
  .bubble { max-width:75%; padding:10px 14px; border-radius:14px; line-height:1.5;
            white-space:pre-wrap; word-wrap:break-word; }
  .user { align-self:flex-end; background:var(--accent); color:#fff; border-bottom-right-radius:4px; }
  .assistant { align-self:flex-start; background:var(--card); border:1px solid #e5e7eb;
               border-bottom-left-radius:4px; }
  .typing { align-self:flex-start; color:#6b7280; font-style:italic; }
  form { display:flex; gap:8px; padding:12px 20px 8px; max-width:820px; width:100%; margin:0 auto; }
  #input { flex:1; padding:12px 14px; border:1px solid #d1d5db; border-radius:12px;
           font-size:15px; outline:none; }
  #input:focus { border-color:var(--accent); }
  button.send, #mic { padding:12px 16px; border:none; border-radius:12px;
                      background:var(--accent); color:#fff; font-size:15px; cursor:pointer; }
  #mic { background:#6b7280; }
  #mic.rec { background:#dc2626; }
  label.speak { display:flex; align-items:center; gap:6px; font-size:13px;
                color:#374151; user-select:none; }
  .hint { text-align:center; font-size:12px; color:#6b7280; padding-bottom:10px; }
</style>
</head>
<body>
<header>
  <h1>🗂️ Task Assistant</h1>
  <div id="stats">Loading stats…</div>
  <button id="refresh" type="button">🔄 Refresh</button>
</header>

<div id="chat"></div>

<form id="form">
  <button type="button" id="mic" title="Voice input">🎤</button>
  <input id="input" autocomplete="off" placeholder="Ask: How many tasks do I have today?">
  <label class="speak"><input type="checkbox" id="speak">🔊 Speak</label>
  <button class="send" type="submit">Send</button>
</form>
<div class="hint">Mic works in Chrome & Safari · Tick 🔊 Speak to hear the replies</div>

<script>
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const form = document.getElementById("form");
const mic = document.getElementById("mic");
const speakToggle = document.getElementById("speak");
const statsEl = document.getElementById("stats");
let history = [];

function addBubble(role, text) {
  const b = document.createElement("div");
  b.className = "bubble " + role;
  b.textContent = text;
  chat.appendChild(b);
  chat.scrollTop = chat.scrollHeight;
}

function showTyping() {
  const t = document.createElement("div");
  t.className = "bubble assistant typing";
  t.id = "typing";
  t.textContent = "Assistant is thinking…";
  chat.appendChild(t);
  chat.scrollTop = chat.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById("typing");
  if (t) t.remove();
}

async function loadStats() {
  try {
    const r = await fetch("/api/stats");
    const s = await r.json();
    statsEl.textContent = "Total: " + s.total + " · Completed: " + s.completed +
                          " · Pending: " + s.pending + " · In Progress: " + s.in_progress;
  } catch (e) {
    statsEl.textContent = "Stats unavailable";
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addBubble("user", text);
  history.push({role: "user", content: text});
  showTyping();
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text, history: history.slice(-20)})
    });
    const data = await res.json();
    hideTyping();
    const reply = data.reply || ("⚠️ " + (data.error || "Unknown error"));
    addBubble("assistant", reply);
    history.push({role: "assistant", content: reply});
    if (speakToggle.checked && "speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(reply);
      u.lang = "en-US";
      speechSynthesis.speak(u);
    }
  } catch (err) {
    hideTyping();
    addBubble("assistant", "⚠️ Network error: " + err);
  }
  loadStats();
});

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
  const rec = new SR();
  rec.lang = "en-US";
  rec.interimResults = false;
  rec.onresult = (e) => {
    input.value = e.results[0][0].transcript;
    form.requestSubmit();
  };
  rec.onstart = () => mic.classList.add("rec");
  rec.onend = () => mic.classList.remove("rec");
  rec.onerror = () => mic.classList.remove("rec");
  mic.addEventListener("click", () => {
    try { rec.start(); } catch (err) {}
  });
} else {
  mic.style.display = "none";
}

document.getElementById("refresh").addEventListener("click", loadStats);
loadStats();
</script>
</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return PAGE


@app.route("/api/stats")
def api_stats():
    """Header er live task stats."""
    try:
        tasks = load_database()["tasks"]
    except Exception:
        return jsonify({"total": 0, "completed": 0, "pending": 0, "in_progress": 0})

    return jsonify({
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t["status"].lower() == "completed"),
        "pending": sum(1 for t in tasks if t["status"].lower() == "pending"),
        "in_progress": sum(1 for t in tasks if t["status"].lower() == "in_progress"),
    })


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Browser theke question nei, OpenAI ke live snapshot shoho pathai."""
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "Empty message."})

    clean_history = [
        {"role": h.get("role", "user"), "content": h.get("content", "")}
        for h in history
        if isinstance(h, dict)
    ]

    try:
        reply = _answer_question(message, clean_history)
        return jsonify({"reply": reply})
    except Exception as exc:
        return jsonify({"error": f"{type(exc).__name__}: {exc}"})


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("\n🌐 Task Assistant web UI:  http://127.0.0.1:5050\n")
    app.run(host="127.0.0.1", port=5050, debug=False)