// Products catalog rendering and filtering logic
document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("products-container");
  const filterBtns = document.querySelectorAll(".filter-chip");

  if (!container) return;

  container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">Loading royal collection...</div>`;

  const products = await QueenShebaAPI.getProducts();

  function render(items) {
    if (!items || items.length === 0) {
      container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No products found in this category.</div>`;
      return;
    }

    container.innerHTML = items.map(p => `
      <article class="product-card" data-category="${p.category}">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="product-icon">${getCategoryIcon(p.category)}</span>
            <span class="product-badge">${p.badge || p.category}</span>
          </div>
          <h3 class="product-name">${p.name}</h3>
          <p class="product-desc">${p.description}</p>
          <ul class="product-features">
            ${(p.features || []).map(f => `<li>${f}</li>`).join("")}
          </ul>
        </div>
        <div class="product-footer">
          <div>
            <div class="product-price">$${p.price}</div>
            <div class="product-stock">● In Stock: ${p.stock} units</div>
          </div>
          <a href="/assistant?prompt=Tell me more about the ${encodeURIComponent(p.name)}" class="btn btn-outline" style="padding: 6px 14px; font-size: 0.8rem;">
            Ask AI ✦
          </a>
        </div>
      </article>
    `).join("");
  }

  render(products);

  // Category filter handlers if present
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const cat = btn.getAttribute("data-category");
      if (!cat || cat === "all") {
        render(products);
      } else {
        render(products.filter(p => p.category.toLowerCase() === cat.toLowerCase()));
      }
    });
  });
});
