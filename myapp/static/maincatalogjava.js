document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const statusSelect = document.getElementById('statusSelect');
    const tableShowAll = document.getElementById('tableShowAll');
    const tableAvailable = document.getElementById('tableRegular');
    const tableUnavailable = document.getElementById('tableDamaged');
    const rowsShowAll = tableShowAll.getElementsByTagName('tr');
    const rowsAvailable = tableAvailable.getElementsByTagName('tr');
    const rowsUnavailable = tableUnavailable.getElementsByTagName('tr');

    // Function to filter tables
    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase();
        const statusFilter = statusSelect.value.toLowerCase();

        // Show tables based on selection
        if (statusFilter === 'showall') {
            tableShowAll.style.display = '';
            tableAvailable.style.display = 'none';
            tableUnavailable.style.display = 'none';
        } else if (statusFilter === 'available') {
            tableShowAll.style.display = 'none';
            tableAvailable.style.display = '';
            tableUnavailable.style.display = 'none';
        } else if (statusFilter === 'unavailable') {
            tableShowAll.style.display = 'none';
            tableAvailable.style.display = 'none';
            tableUnavailable.style.display = '';
        }

        // Filter Show All table
        for (let i = 1; i < rowsShowAll.length; i++) {
            const cells = rowsShowAll[i].getElementsByTagName('td');
            let matchesSearch = false;
            let matchesStatus = false;

            if (cells.length > 0) {
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].innerText.toLowerCase().includes(searchTerm)) {
                        matchesSearch = true;
                        break;
                    }
                }
                const statusText = cells[2].innerText.toLowerCase();
                matchesStatus = (statusFilter === 'showall') || (statusFilter === statusText);

                if (matchesSearch && matchesStatus) {
                    rowsShowAll[i].style.display = '';
                } else {
                    rowsShowAll[i].style.display = 'none';
                }
            }
        }

        // Filter Available table
        for (let i = 1; i < rowsAvailable.length; i++) {
            const cells = rowsAvailable[i].getElementsByTagName('td');
            let matchesSearch = false;

            if (cells.length > 0) {
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].innerText.toLowerCase().includes(searchTerm)) {
                        matchesSearch = true;
                        break;
                    }
                }

                if (matchesSearch) {
                    rowsAvailable[i].style.display = '';
                } else {
                    rowsAvailable[i].style.display = 'none';
                }
            }
        }

        // Filter Unavailable table
        for (let i = 1; i < rowsUnavailable.length; i++) {
            const cells = rowsUnavailable[i].getElementsByTagName('td');
            let matchesSearch = false;

            if (cells.length > 0) {
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].innerText.toLowerCase().includes(searchTerm)) {
                        matchesSearch = true;
                        break;
                    }
                }

                if (matchesSearch) {
                    rowsUnavailable[i].style.display = '';
                } else {
                    rowsUnavailable[i].style.display = 'none';
                }
            }
        }
    }

    // Add event listeners for search and status select
    searchInput.addEventListener('input', filterTable);
    statusSelect.addEventListener('change', filterTable);
});
