const tabs = document.querySelectorAll('.invoice-tabs .tab');
const tables = document.querySelectorAll('.invoice-table');
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
            document.querySelector('[data-table="invoices"]').classList.remove('hidden');
        }
    });
});

/* Row click navigation */
document.querySelectorAll('.invoice-table tr.clickable').forEach(row => {
    row.addEventListener('click', (e) => {
        if (e.target.type === 'checkbox') return;

        // placeholder routes
        window.location.href = '/invoices/view';
    });
});

/* Checkbox logic */
document.addEventListener('change', () => {
    const checked = document.querySelectorAll('tbody input[type="checkbox"]:checked').length;
    actionButtons.forEach(btn => {
        btn.disabled = checked === 0;
    });
});
