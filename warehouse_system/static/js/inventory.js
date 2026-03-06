const tabs = document.querySelectorAll('.inventory-tabs .tab');
const tables = document.querySelectorAll('.inventory-table');
const actionButtons = document.querySelectorAll('.secondary-action');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const selected = tab.dataset.tab;

        tables.forEach(table => {
            table.classList.add('hidden');
        });

        if (selected === 'customers') {
            document.querySelector('[data-table="customers"]').classList.remove('hidden');
        } else {
            document.querySelector('[data-table="inventory"]').classList.remove('hidden');
        }
    });
});

const searchInput = document.getElementById("inventory-search")

searchInput.addEventListener("keydown", async (e) => {

    if (e.key !== "Enter") return

    const query = searchInput.value.trim()

    const res = await fetch(`/inventory/search?q=${query}`)
    const data = await res.json()

    if (data.length === 1) {
        window.location = `/product/${data[0].product_id}`
    }

})

let timer

searchInput.addEventListener("input", () => {

    clearTimeout(timer)

    timer = setTimeout(async () => {

        const query = searchInput.value.trim()

        if (query.length === 0) {
            window.location.reload()
            return
        }

        if (query.length < 2) return

        const res = await fetch(`/inventory/search?q=${query}`)
        const data = await res.json()

        updateTable(data)

    }, 250)

})

function updateTable(products){

    const tbody = document.querySelector(".inventory-table tbody")
    tbody.innerHTML = ""

    products.forEach(p => {

        const row = document.createElement("tr")
        row.classList.add("clickable")

        row.onclick = () => {
            window.location = `/product/${p.product_id}`
        }

        row.innerHTML = `
            <td>${p.product_code}</td>
            <td>${p.stock_code}</td>
            <td>${p.description}</td>
            <td>${p.capacity}</td>
            <td>${p.total_stock}</td>
            <td>${p.pallet_count}</td>
        `

        tbody.appendChild(row)
    })
}