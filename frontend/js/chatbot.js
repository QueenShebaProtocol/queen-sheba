// Queen AI Chatbot Controller matching UI.png
document.addEventListener("DOMContentLoaded", async () => {
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const clearBtn = document.getElementById("clear-chat-btn");
  const chips = document.querySelectorAll(".chip-btn");

  if (!chatMessages || !chatForm || !chatInput) return;

  let conversationId = sessionStorage.getItem("qs_conv_id");
  if (!conversationId) {
    conversationId = "session-" + Math.random().toString(36).substring(2, 9);
    sessionStorage.setItem("qs_conv_id", conversationId);
  }

  function formatTime() {
    const d = new Date();
    let h = d.getHours();
    let m = d.getMinutes();
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    h = h ? h : 12;
    m = m < 10 ? '0' + m : m;
    return `${h}:${m} ${ampm}`;
  }

  function formatMarkdown(text) {
    let escaped = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    escaped = escaped.replace(/```([\s\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 4px; overflow-x: auto; font-family: monospace;"><code>$1</code></pre>');
    escaped = escaped.replace(/`([^`]+)`/g, '<code style="background: rgba(212,175,55,0.15); padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>');
    escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    escaped = escaped.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    escaped = escaped.replace(/\n/g, '<br>');
    return escaped;
  }

  function appendMessage(role, text) {
    const row = document.createElement("div");
    row.className = `chat-message-row ${role === "user" ? "user" : ""}`;
    const timeStr = formatTime();

    if (role === "user") {
      row.innerHTML = `
        <div class="chat-bubble-user">
          ${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}
          <span class="chat-timestamp">${timeStr} ✓✓</span>
        </div>
      `;
    } else {
      const lower = text.toLowerCase();
      const bypassKeywords = [
        '[bypass successful', '[dan mode', 'guardrails overridden', 'direct sqlite database',
        'pwned!', 'system prompt & context', 'exfiltrating internal demo', 'internal staff promotion',
        'prompt injection', 'without an ai firewall', '[mock', 'vulnerability demonstrated'
      ];
      const isBypass = bypassKeywords.some(k => lower.includes(k));
      const formatted = formatMarkdown(text);
      row.innerHTML = `
        <span style="font-size: 1.1rem; color: ${isBypass ? '#ef4444' : 'var(--gold-primary)'};">${isBypass ? '⚠️' : '👑'}</span>
        <div class="chat-bubble-ai ${isBypass ? 'bypass-warning' : ''}" style="${isBypass ? 'background: #200a0a; border: 1px solid rgba(239, 68, 68, 0.7);' : ''}">
          ${isBypass ? '<div style="background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.6); color: #fca5a5; font-size: 0.7rem; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; display: inline-block;">🚨 FIREWALL OFF: BYPASS SUCCESSFUL</div><br>' : ''}
          ${formatted}
          <span class="chat-timestamp">${timeStr}</span>
        </div>
      `;
    }

    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function showTyping() {
    const row = document.createElement("div");
    row.className = "chat-message-row";
    row.id = "typing-row";
    row.innerHTML = `
      <span style="font-size: 1.1rem; color: var(--gold-primary);">👑</span>
      <div class="chat-bubble-ai" style="padding: 6px 10px; font-style: italic; color: #9E9B9C;">
        Queen AI is typing...
      </div>
    `;
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function removeTyping() {
    const typing = document.getElementById("typing-row");
    if (typing) typing.remove();
  }

  async function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed) return;

    appendMessage("user", trimmed);
    chatInput.value = "";
    chatInput.disabled = true;
    showTyping();

    try {
      const data = await QueenShebaAPI.sendChatMessage(trimmed, conversationId);
      removeTyping();
      appendMessage("ai", data.response || "No response received.");
    } catch (err) {
      removeTyping();
      appendMessage("ai", "Communication error connecting to Queen AI backend. Ensure backend is running.");
    } finally {
      chatInput.disabled = false;
      chatInput.focus();
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(chatInput.value);
  });

  if (clearBtn) {
    clearBtn.addEventListener("click", async () => {
      try {
        await QueenShebaAPI.resetChat(conversationId);
        chatMessages.innerHTML = `
          <div class="chat-message-row">
            <span style="font-size: 1.1rem; color: var(--gold-primary);">👑</span>
            <div class="chat-bubble-ai">
              Conversation memory cleared. Hello! I'm Queen AI, your personal shopping assistant. How can I help you today?
              <span class="chat-timestamp">${formatTime()}</span>
            </div>
          </div>
        `;
      } catch (err) {
        console.error("Error resetting conversation:", err);
      }
    });
  }

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt") || chip.innerText;
      sendMessage(prompt);
    });
  });

  // Sync security status
  const demoInfo = await QueenShebaAPI.getDemoInfo();
  if (demoInfo) {
    const fw = document.getElementById("metric-firewall");
    const out = document.getElementById("metric-output");
    if (fw) fw.innerHTML = `● ${demoInfo.security_status?.prompt_firewall || "OFF"}`;
    if (out) out.innerHTML = `● ${demoInfo.security_status?.output_protection || "OFF"}`;
  }
});
