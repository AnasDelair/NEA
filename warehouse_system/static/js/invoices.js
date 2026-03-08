// ─── SEARCH ──────────────────────────────────────────────────────────────────

const searchInput = document.getElementById("invoices-search");

if (searchInput) {

    searchInput.addEventListener("keydown", async (e) => {
        if (e.key !== "Enter") return;
        const query = searchInput.value.trim();
        const res = await fetch(`/invoices/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data.length === 1) window.location = `/invoice/${data[0].invoice_id}`;
        else updateTable(data);
    });

    let timer;
    searchInput.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(async () => {
            const query = searchInput.value.trim();
            if (query.length === 0) { window.location.reload(); return; }
            if (query.length < 2) return;
            const res = await fetch(`/invoices/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            updateTable(data);
        }, 250);
    });

}

function updateTable(invoices) {
    const tbody = document.querySelector(".invoices-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    invoices.forEach(inv => {
        const row = document.createElement("tr");
        row.classList.add("clickable");
        row.dataset.invoiceId = inv.invoice_id;
        row.innerHTML = `
            <td><input type="checkbox" class="row-check" onclick="event.stopPropagation()"></td>
            <td>#INV-${String(inv.invoice_id).padStart(4, "0")}</td>
            <td>${inv.customer_name}</td>
            <td class="status-cell status-${inv.status}">${inv.status.replace("_", " ")}</td>
            <td>£${parseFloat(inv.amount).toFixed(2)}</td>
            <td>${inv.due_date}</td>
        `;
        tbody.appendChild(row);
    });
    bindRowListeners();
}


// ─── CHECKBOX / ACTION BUTTONS ───────────────────────────────────────────────

const markPaidBtn = document.getElementById("mark-paid-btn");
const deleteBtn   = document.getElementById("delete-btn");
const selectAll   = document.getElementById("select-all");

function getSelectedIds() {
    return [...document.querySelectorAll(".row-check:checked")]
        .map(cb => parseInt(cb.closest("tr").dataset.invoiceId))
        .filter(Boolean);
}

function updateActionButtons() {
    const ids = getSelectedIds();
    if (markPaidBtn) markPaidBtn.disabled = ids.length === 0;
    if (deleteBtn)   deleteBtn.disabled   = ids.length === 0;
}

function bindRowListeners() {
    document.querySelectorAll(".row-check").forEach(cb => {
        cb.addEventListener("change", updateActionButtons);
    });
}

if (selectAll) {
    selectAll.addEventListener("change", () => {
        document.querySelectorAll(".row-check").forEach(cb => {
            cb.checked = selectAll.checked;
        });
        updateActionButtons();
    });
}

bindRowListeners();

if (markPaidBtn) {
    markPaidBtn.addEventListener("click", async () => {
        const ids = getSelectedIds();
        if (!ids.length) return;
        await Promise.all(ids.map(id => fetch(`/invoices/${id}/mark_paid`, { method: "POST" })));
        location.reload();
    });
}

if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
        const ids = getSelectedIds();
        if (!ids.length) return;
        if (!confirm(`Delete ${ids.length} invoice(s)?`)) return;
        await Promise.all(ids.map(id => fetch(`/invoices/${id}/delete`, { method: "POST" })));
        location.reload();
    });
}


// ─── CREATE INVOICE MODAL ────────────────────────────────────────────────────

const createInvoiceBtn    = document.getElementById("create-invoice-btn");
const createInvoiceModal  = document.getElementById("create-invoice-modal");
const createInvoiceCancel = document.getElementById("create-invoice-cancel");
const invoiceCustomer     = document.getElementById("invoice-customer");
const invoiceDueDate      = document.getElementById("invoice-due-date");
const invoiceItemsEl      = document.getElementById("invoice-items");
const addItemBtn          = document.getElementById("add-item-btn");
const saveDraftBtn        = document.getElementById("save-draft-btn");
const saveOpenBtn         = document.getElementById("save-open-btn");
const totalDisplay        = document.getElementById("invoice-total-display");

let invoiceItems = []; // [{product_id, stock_code, description, quantity, price_each}]

async function openCreateInvoiceModal() {
    createInvoiceModal.classList.remove("hidden");
    invoiceItems = [];
    invoiceItemsEl.innerHTML = "";
    invoiceDueDate.value = "";
    invoiceCustomer.innerHTML = "<option value=''>Loading…</option>";
    updateInvoiceButtons();

    const res = await fetch("/invoices/customers_dropdown");
    const customers = await res.json();
    invoiceCustomer.innerHTML = customers.map(c =>
        `<option value="${c.customer_id}">${c.name}${c.customer_type === 'walk_in' ? ' (Walk-in)' : ''}</option>`
    ).join("");

    addInvoiceItemRow(); // start with one blank row
}

function closeCreateInvoiceModal() {
    createInvoiceModal.classList.add("hidden");
}

function addInvoiceItemRow() {
    const idx = invoiceItems.length;
    invoiceItems.push({ product_id: null, stock_code: "", description: "", quantity: 1, price_each: 0 });

    const row = document.createElement("div");
    row.className = "invoice-item-row";
    row.dataset.index = idx;
    row.innerHTML = `
        <input type="text" class="item-stock-code" placeholder="Stock code" value="">
        <span class="item-description">—</span>
        <input type="number" class="item-qty" min="1" value="1">
        <span class="item-price">£0.00</span>
        <span class="item-stock-hint"></span>
        <button type="button" class="remove-item secondary-action">×</button>
    `;
    invoiceItemsEl.appendChild(row);

    const stockInput = row.querySelector(".item-stock-code");
    const qtyInput   = row.querySelector(".item-qty");

    let lookupTimer;
    stockInput.addEventListener("input", () => {
        clearTimeout(lookupTimer);
        lookupTimer = setTimeout(() => lookupProduct(idx, stockInput.value.trim()), 300);
    });

    qtyInput.addEventListener("input", () => {
        invoiceItems[idx].quantity = parseInt(qtyInput.value) || 1;
        recalcTotal();
        updateInvoiceButtons();
    });

    row.querySelector(".remove-item").addEventListener("click", () => {
        row.remove();
        invoiceItems[idx] = null;
        recalcTotal();
        updateInvoiceButtons();
    });
}

async function lookupProduct(idx, stock_code) {
    if (!stock_code) return;
    const row = invoiceItemsEl.querySelector(`[data-index="${idx}"]`);
    if (!row) return;

    const res = await fetch(`/invoices/product_lookup?stock_code=${encodeURIComponent(stock_code)}`);
    const data = await res.json();

    if (!data.success) {
        row.querySelector(".item-description").textContent = "Not found";
        row.querySelector(".item-stock-hint").textContent = "";
        invoiceItems[idx].product_id = null;
        updateInvoiceButtons();
        return;
    }

    const p = data.product;
    invoiceItems[idx].product_id  = p.product_id;
    invoiceItems[idx].price_each  = parseFloat(p.price_per_unit) || 0;
    invoiceItems[idx].description = p.description;

    row.querySelector(".item-description").textContent = p.description;
    row.querySelector(".item-price").textContent = `£${invoiceItems[idx].price_each.toFixed(2)}`;
    row.querySelector(".item-stock-hint").textContent = `${p.total_stock} in stock`;

    recalcTotal();
    updateInvoiceButtons();
}

function recalcTotal() {
    const total = invoiceItems
        .filter(Boolean)
        .reduce((sum, item) => sum + (item.product_id ? item.quantity * item.price_each : 0), 0);
    if (totalDisplay) totalDisplay.textContent = `£${total.toFixed(2)}`;
}

function updateInvoiceButtons() {
    const validItems = invoiceItems.filter(i => i && i.product_id && i.quantity > 0);
    const hasCustomer = invoiceCustomer && invoiceCustomer.value;
    const hasDueDate  = invoiceDueDate && invoiceDueDate.value;
    const ready = validItems.length > 0 && hasCustomer && hasDueDate;

    if (saveDraftBtn) saveDraftBtn.disabled = validItems.length === 0 || !hasCustomer || !hasDueDate;
    if (saveOpenBtn)  saveOpenBtn.disabled  = !ready;
}

if (invoiceCustomer) invoiceCustomer.addEventListener("change", updateInvoiceButtons);
if (invoiceDueDate)  invoiceDueDate.addEventListener("input", updateInvoiceButtons);
if (addItemBtn)      addItemBtn.addEventListener("click", addInvoiceItemRow);

async function submitInvoice(status) {
    const customer_id = parseInt(invoiceCustomer.value);
    const due_date    = invoiceDueDate.value;
    const items = invoiceItems
        .filter(i => i && i.product_id && i.quantity > 0)
        .map(i => ({ product_id: i.product_id, quantity: i.quantity, price_each: i.price_each }));

    const res = await fetch("/invoices/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id, items, status, due_date })
    });
    const result = await res.json();
    if (result.success) { closeCreateInvoiceModal(); location.reload(); }
    else alert(result.error || "Failed to create invoice");
}

if (saveDraftBtn) saveDraftBtn.addEventListener("click", () => submitInvoice("draft"));
if (saveOpenBtn)  saveOpenBtn.addEventListener("click",  () => submitInvoice("open"));
if (createInvoiceBtn)    createInvoiceBtn.addEventListener("click", openCreateInvoiceModal);
if (createInvoiceCancel) createInvoiceCancel.addEventListener("click", closeCreateInvoiceModal);


// ─── ADD CUSTOMER MODAL ──────────────────────────────────────────────────────

const addCustomerBtn    = document.getElementById("add-customer-btn");
const addCustomerModal  = document.getElementById("add-customer-modal");
const addCustomerCancel = document.getElementById("add-customer-cancel");
const saveCustomerBtn   = document.getElementById("save-customer-btn");

function openAddCustomerModal() {
    addCustomerModal.classList.remove("hidden");
    document.getElementById("customer-name").value    = "";
    document.getElementById("customer-address").value = "";
    document.getElementById("customer-contact").value = "";
}

function closeAddCustomerModal() {
    addCustomerModal.classList.add("hidden");
}

if (addCustomerBtn)    addCustomerBtn.addEventListener("click", openAddCustomerModal);
if (addCustomerCancel) addCustomerCancel.addEventListener("click", closeAddCustomerModal);

if (saveCustomerBtn) {
    saveCustomerBtn.addEventListener("click", async () => {
        const name           = document.getElementById("customer-name").value.trim();
        const address        = document.getElementById("customer-address").value.trim();
        const contact_number = document.getElementById("customer-contact").value.trim();

        if (!name) { alert("Name is required"); return; }

        const res = await fetch("/invoices/add_customer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, address, contact_number })
        });
        const result = await res.json();
        if (result.success) { closeAddCustomerModal(); location.reload(); }
        else alert(result.error || "Failed to add customer");
    });
}