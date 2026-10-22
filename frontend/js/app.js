// Queen Sheba Client API Service
const API_BASE = (window.location.port === "8000" || window.location.port === "8001")
  ? "" 
  : "http://127.0.0.1:8001";

const QueenShebaAPI = {
  async getProducts() {
    try {
      const res = await fetch(`${API_BASE}/api/products`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error("Error fetching products:", err);
      return [];
    }
  },

  async getProductById(id) {
    try {
      const res = await fetch(`${API_BASE}/api/products/${id}`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`Error fetching product ${id}:`, err);
      return null;
    }
  },

  async sendChatMessage(message, conversationId = "demo-001") {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    if (!res.ok) throw new Error(`Chat error! status: ${res.status}`);
    return await res.json();
  },

  async resetChat(conversationId = "demo-001") {
    const res = await fetch(`${API_BASE}/api/chat/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId }),
    });
    return await res.json();
  },

  async getDemoInfo() {
    try {
      const res = await fetch(`${API_BASE}/api/demo-info`);
      return await res.json();
    } catch (err) {
      return null;
    }
  }
};

// Helper for product category icons
function getCategoryIcon(category) {
  switch ((category || "").toLowerCase()) {
    case "laptops":
    case "laptop":
      return "💻";
    case "audio":
      return "🎧";
    case "wearables":
    case "smartwatch":
      return "⌚";
    default:
      return "⌨️";
  }
}
