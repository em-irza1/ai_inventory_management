// Stockwise frontend. Shows the REAL server error message so problems are easy to find.
const $ = (id) => document.getElementById(id);
let currentSearch = "";

const money = (n) => "PKR " + Number(n || 0).toLocaleString("en-PK", { maximumFractionDigits: 2 });
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function toast(msg, isError = false) {
  const t = $("toast");
  t.textContent = msg;
  t.className = "toast show" + (isError ? " error" : "");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.className = "toast"), 3500);
}

// One helper for every request: returns parsed JSON or throws an Error with the server's message.
async function api(url, method = "GET", body) {
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    throw new Error("Cannot reach the server. Is `py app.py` running, and are you on http://127.0.0.1:5000 ?");
  }
  let data = {};
  try { data = await res.json(); } catch (e) { /* not JSON */ }
  if (!res.ok || data.success === false) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

function renderStats(s) {
  const items = [
    ["Products", s.total_products], ["Units in stock", s.total_units],
    ["Inventory value", money(s.inventory_value)], ["Low stock", s.low_stock], ["Out of stock", s.out_of_stock],
  ];
  $("stats").innerHTML = items.map(([l, v]) => `<div class="stat"><span>${l}</span><strong>${esc(v)}</strong></div>`).join("");
}

function statusTag(s) {
  const cls = s === "In stock" ? "ok" : s === "Low stock" ? "low" : "out";
  return `<span class="tag ${cls}">${esc(s)}</span>`;
}

let productCache = [];
function renderRows(products) {
  productCache = products;
  if (!products.length) {
    $("rows").innerHTML = `<tr><td colspan="8" class="empty">No products yet. Add your first product using the form above.</td></tr>`;
    return;
  }
  $("rows").innerHTML = products.map((p) => `
    <tr>
      <td>${esc(p.product_id)}</td>
      <td>${esc(p.name)}${p.type === "perishable" ? `<br><small>Expires ${esc(p.expiry_date || "not set")}</small>` : ""}</td>
      <td>${esc(p.category)}</td><td>${money(p.price)}</td><td>${esc(p.quantity)}</td>
      <td>${money(p.total_value)}</td><td>${statusTag(p.stock_status)}</td>
      <td class="actions-cell">
        <button class="btn small" data-edit="${esc(p.product_id)}">Edit</button>
        <button class="btn small danger" data-del="${esc(p.product_id)}">Delete</button>
      </td>
    </tr>`).join("");
}

async function loadProducts() {
  try {
    const data = await api("/api/products" + (currentSearch ? "?q=" + encodeURIComponent(currentSearch) : ""));
    renderStats(data.stats);
    renderRows(data.products);
  } catch (e) { toast(e.message, true); }
}

async function loadHealth() {
  try {
    const h = await api("/api/health");
    $("aiBadge").textContent = h.ai_configured ? "AI ready: " + h.model : "AI not configured";
    $("aiBadge").className = "badge " + (h.ai_configured ? "on" : "off");
  } catch (e) { $("aiBadge").textContent = "Server unreachable"; $("aiBadge").className = "badge off"; }
}

// ---------- form ----------
function resetForm() {
  $("productForm").reset();
  $("productId").value = "";
  $("formTitle").textContent = "Add a product";
  $("saveBtn").textContent = "Add product";
  $("cancelBtn").hidden = true;
  $("expiryWrap").hidden = true;
}

$("type").addEventListener("change", () => ($("expiryWrap").hidden = $("type").value !== "perishable"));
$("cancelBtn").addEventListener("click", resetForm);

$("productForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    name: $("name").value, category: $("category").value, price: $("price").value,
    quantity: $("quantity").value, reorder_level: $("reorder_level").value,
    description: $("description").value, type: $("type").value, expiry_date: $("expiry_date").value,
  };
  const id = $("productId").value;
  try {
    await api(id ? `/api/products/${encodeURIComponent(id)}` : "/api/products", id ? "PUT" : "POST", body);
    toast(id ? "Product updated." : "Product added.");
    resetForm();
    loadProducts();
  } catch (err) { toast(err.message, true); }
});

$("rows").addEventListener("click", async (e) => {
  const editId = e.target.dataset.edit, delId = e.target.dataset.del;
  if (editId) {
    const p = productCache.find((x) => x.product_id === editId);
    if (!p) return;
    $("productId").value = p.product_id; $("name").value = p.name; $("category").value = p.category;
    $("price").value = p.price; $("quantity").value = p.quantity; $("reorder_level").value = p.reorder_level;
    $("description").value = p.description; $("type").value = p.type; $("expiry_date").value = p.expiry_date || "";
    $("expiryWrap").hidden = p.type !== "perishable";
    $("formTitle").textContent = "Edit product"; $("saveBtn").textContent = "Save changes"; $("cancelBtn").hidden = false;
    $("formCard").scrollIntoView({ behavior: "smooth" });
  }
  if (delId && confirm("Delete this product? This cannot be undone.")) {
    try { await api(`/api/products/${encodeURIComponent(delId)}`, "DELETE"); toast("Product deleted."); loadProducts(); }
    catch (err) { toast(err.message, true); }
  }
});

let searchTimer;
$("search").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { currentSearch = e.target.value.trim(); loadProducts(); }, 250);
});

// ---------- AI ----------
async function runAI(button, url, body, target) {
  const label = button.textContent;
  button.disabled = true; button.textContent = "Working...";
  const out = target || $("aiOutput");
  if (out === $("aiOutput")) { out.className = "ai-out"; out.textContent = "Thinking..."; }
  try {
    const data = await api(url, "POST", body);
    return data.result;
  } catch (err) {
    if (out === $("aiOutput")) { out.className = "ai-out error"; out.textContent = err.message; }
    toast(err.message, true);
    return null;
  } finally { button.disabled = false; button.textContent = label; }
}

$("analyzeBtn").addEventListener("click", async (e) => {
  const r = await runAI(e.target, "/api/ai/analyze", {}); if (r) $("aiOutput").textContent = r;
});
$("reorderBtn").addEventListener("click", async (e) => {
  const r = await runAI(e.target, "/api/ai/reorder", {}); if (r) $("aiOutput").textContent = r;
});
$("askForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const r = await runAI(e.submitter || e.target.querySelector("button"), "/api/ai/ask", { question: $("question").value });
  if (r) $("aiOutput").textContent = r;
});
$("aiDescBtn").addEventListener("click", async (e) => {
  const r = await runAI(e.target, "/api/ai/description", {
    name: $("name").value, category: $("category").value, price: $("price").value, details: $("description").value,
  }, $("toast"));
  if (r) { $("description").value = r; toast("Description written. Edit it if you like."); }
});

loadHealth();
loadProducts();
