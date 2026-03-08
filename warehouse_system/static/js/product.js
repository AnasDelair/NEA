// ─── ADD STOCK MODAL ────────────────────────────────────────────────────────

const addBtn      = document.getElementById("add-stock");
const addModal    = document.getElementById("add-stock-modal");
const addTitle    = document.getElementById("add-modal-title");
const totalInput  = document.getElementById("modal-total");
const palletList  = document.getElementById("pallet-list");
const addSubmit   = document.getElementById("add-modal-submit");
const addCancel   = document.getElementById("add-modal-cancel");
const palletCountInput = document.getElementById("modal-pallets");

let addPallets = [];

function openAddModal() {
    addModal.classList.remove("hidden");
    totalInput.value = 0;
    palletCountInput.value = 1;
    addPallets = [];
    palletList.innerHTML = "";
    addSubmit.disabled = true;
}

function closeAddModal() {
    addModal.classList.add("hidden");
}

function updateAddPalletRows() {
    palletList.innerHTML = "";
    addPallets.forEach((qty, idx) => {
        const row = document.createElement("div");
        row.className = "pallet-row";
        row.innerHTML = `
            <span>Pallet ${idx + 1}:</span>
            <input type="number" min="0" value="${qty}" data-index="${idx}">
            <button type="button" class="remove-pallet">×</button>
        `;
        palletList.appendChild(row);
    });
    validateAddTotal();
}

function distributeAddPallets() {
    const total = parseInt(totalInput.value) || 0;
    const numPallets = Math.max(parseInt(palletCountInput.value) || 1, 1);
    addPallets = Array(numPallets).fill(Math.floor(total / numPallets));
    let remainder = total - addPallets.reduce((a, b) => a + b, 0);
    for (let i = 0; remainder > 0 && i < addPallets.length; i++) { addPallets[i]++; remainder--; }
    updateAddPalletRows();
}

function validateAddTotal() {
    const total = parseInt(totalInput.value) || 0;
    const sum = addPallets.reduce((a, b) => a + b, 0);
    addSubmit.disabled = total !== sum || total === 0;
}

palletList.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-pallet")) {
        const idx = parseInt(e.target.previousElementSibling.dataset.index);
        addPallets.splice(idx, 1);
        updateAddPalletRows();
    }
});

palletList.addEventListener("input", (e) => {
    if (e.target.tagName === "INPUT") {
        addPallets[parseInt(e.target.dataset.index)] = parseInt(e.target.value) || 0;
        validateAddTotal();
    }
});

totalInput.addEventListener("input", distributeAddPallets);
palletCountInput.addEventListener("input", distributeAddPallets);

// "Add Pallet" button injected below the list
const addPalletBtn = document.createElement("button");
addPalletBtn.textContent = "+ Add Pallet";
addPalletBtn.type = "button";
addPalletBtn.className = "secondary-action";
addPalletBtn.addEventListener("click", () => { addPallets.push(0); updateAddPalletRows(); });
palletList.parentNode.insertBefore(addPalletBtn, palletList.nextSibling);

addBtn.addEventListener("click", openAddModal);
addCancel.addEventListener("click", closeAddModal);

addSubmit.addEventListener("click", async () => {
    const total = parseInt(totalInput.value);
    if (total !== addPallets.reduce((a, b) => a + b, 0)) {
        alert("Total does not match sum of pallets");
        return;
    }
    try {
        const res = await fetch(`/product/${productId}/add_stock`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ total, pallets: addPallets })
        });
        const result = await res.json();
        if (result.success) { closeAddModal(); location.reload(); }
        else alert(result.error || "Error adding stock");
    } catch (err) {
        console.error(err);
        alert("Failed to communicate with server");
    }
});


// ─── REMOVE STOCK MODAL ──────────────────────────────────────────────────────

const removeBtn        = document.getElementById("remove-stock");
const removeModal      = document.getElementById("remove-stock-modal");
const removeTotalInput = document.getElementById("remove-modal-total");
const removePalletList = document.getElementById("remove-pallet-list");
const removeSubmit     = document.getElementById("remove-modal-submit");
const removeCancel     = document.getElementById("remove-modal-cancel");
const removeLoading    = document.getElementById("remove-modal-loading");

let livePallets = [];   // fetched from server: [{pallet_id, location_id, quantity, date_stored}]
let removeAmounts = {}; // pallet_id -> amount to remove

async function openRemoveModal() {
    removeModal.classList.remove("hidden");
    removeTotalInput.value = 0;
    removeAmounts = {};
    removePalletList.innerHTML = "";
    removeSubmit.disabled = true;
    removeLoading.classList.remove("hidden");

    try {
        const res = await fetch(`/product/${productId}/pallets`);
        const data = await res.json();
        livePallets = data.pallets || [];
    } catch (err) {
        console.error(err);
        alert("Failed to load pallets");
        closeRemoveModal();
        return;
    }

    removeLoading.classList.add("hidden");

    if (livePallets.length === 0) {
        removePalletList.innerHTML = "<p class='no-pallets'>No stock on any pallets.</p>";
        return;
    }

    livePallets.forEach(p => { removeAmounts[p.pallet_id] = 0; });
    renderRemovePallets();
}

function closeRemoveModal() {
    removeModal.classList.add("hidden");
}

function renderRemovePallets() {
    removePalletList.innerHTML = "";

    livePallets.forEach(p => {
        const removing = removeAmounts[p.pallet_id] || 0;
        const remaining = p.quantity - removing;

        const row = document.createElement("div");
        row.className = "remove-pallet-row";
        row.innerHTML = `
            <div class="remove-pallet-info">
                <span class="pallet-label">Pallet #${p.pallet_id}</span>
                <span class="pallet-location">Location ${p.location_id}</span>
                <span class="pallet-stock">In stock: <strong>${p.quantity}</strong></span>
            </div>
            <div class="remove-pallet-controls">
                <label>Remove:</label>
                <input
                    type="number"
                    min="0"
                    max="${p.quantity}"
                    value="${removing}"
                    data-pallet-id="${p.pallet_id}"
                    data-max="${p.quantity}"
                >
                <span class="pallet-remaining ${remaining < 0 ? 'over' : ''}">
                    → ${Math.max(remaining, 0)} left
                </span>
            </div>
        `;
        removePalletList.appendChild(row);
    });

    validateRemoveTotal();
}

removePalletList.addEventListener("input", (e) => {
    if (e.target.tagName === "INPUT") {
        const palletId = parseInt(e.target.dataset.palletId);
        const max = parseInt(e.target.dataset.max);
        let val = parseInt(e.target.value) || 0;
        if (val > max) { val = max; e.target.value = max; }
        removeAmounts[palletId] = val;
        renderRemovePallets(); // re-render to update "left" counts
    }
});

removeTotalInput.addEventListener("input", validateRemoveTotal);

function validateRemoveTotal() {
    const total = parseInt(removeTotalInput.value) || 0;
    const sum = Object.values(removeAmounts).reduce((a, b) => a + b, 0);
    const allValid = livePallets.every(p => (removeAmounts[p.pallet_id] || 0) <= p.quantity);
    removeSubmit.disabled = total !== sum || total === 0 || !allValid;

    const diff = sum - total;

    // Always reset both, then apply what's needed
    removeTotalInput.classList.remove("input-over", "input-under");
    if (diff > 0) removeTotalInput.classList.add("input-over");
    else if (diff < 0 && total > 0) removeTotalInput.classList.add("input-under");

    document.getElementById("remove-sum-hint").textContent =
        total === 0 ? "" :
        diff === 0  ? `Pallet total matches` :
        diff > 0    ? `Pallets exceed total by ${diff}` :
                      `${Math.abs(diff)} more to allocate`;
}

removeBtn.addEventListener("click", openRemoveModal);
removeCancel.addEventListener("click", closeRemoveModal);

removeSubmit.addEventListener("click", async () => {
    const total = parseInt(removeTotalInput.value);

    const palletUpdates = livePallets
        .filter(p => (removeAmounts[p.pallet_id] || 0) > 0)
        .map(p => ({ pallet_id: p.pallet_id, quantity: removeAmounts[p.pallet_id] }));

    const sum = palletUpdates.reduce((a, b) => a + b.quantity, 0);
    if (sum !== total) {
        alert("Total does not match sum of pallet removals");
        return;
    }

    try {
        const res = await fetch(`/product/${productId}/remove_stock`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ total, pallets: palletUpdates })
        });
        const result = await res.json();
        if (result.success) { closeRemoveModal(); location.reload(); }
        else alert(result.error || "Error removing stock");
    } catch (err) {
        console.error(err);
        alert("Failed to communicate with server");
    }
});