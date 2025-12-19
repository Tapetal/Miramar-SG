const body = document.querySelector("body");
const sidebar = body.querySelector("nav");
const sidebarToggle = body.querySelector(".sidebar-toggle");
const modeToggle = body.querySelector(".mode-toggle");
const modeIcon = body.querySelector("#mode-icon");
const darkModeToggle = body.querySelector("#dark-mode-toggle");
const searchInput = body.querySelector(".search-box input");

// Initialize dark mode from localStorage
let getMode = localStorage.getItem("mode");
if (getMode && getMode === "dark") {
    body.classList.add("dark");
    modeIcon.classList.replace("uil-moon", "uil-sun");
}

// Initialize sidebar state from localStorage
let getStatus = localStorage.getItem("status");
if (getStatus && getStatus === "close") {
    sidebar.classList.add("close");
}

// Dark mode toggle functionality
modeToggle.addEventListener("click", () => {
    body.classList.toggle("dark");
    if (body.classList.contains("dark")) {
        localStorage.setItem("mode", "dark");
        modeIcon.classList.replace("uil-moon", "uil-sun");
    } else {
        localStorage.setItem("mode", "light");
        modeIcon.classList.replace("uil-sun", "uil-moon");
    }
});

// Alternative dark mode toggle (clicking the link)
if (darkModeToggle) {
    darkModeToggle.addEventListener("click", (e) => {
        e.preventDefault();
        modeToggle.click();
    });
}

// Sidebar toggle functionality
sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
    if (sidebar.classList.contains("close")) {
        localStorage.setItem("status", "close");
    } else {
        localStorage.setItem("status", "open");
    }
});

// Search functionality for dashboard table
if (searchInput) {
    searchInput.addEventListener("input", function() {
        const searchTerm = this.value.toLowerCase();
        const tableRows = document.querySelectorAll(".modern-table tbody tr");
        
        tableRows.forEach(row => {
            // Skip the "no data" row
            if (row.querySelector('.no-data')) {
                return;
            }
            
            const rowText = row.textContent.toLowerCase();
            
            if (rowText.includes(searchTerm)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
        
        // Show "no results" message if all rows are hidden
        const visibleRows = Array.from(tableRows).filter(row => 
            row.style.display !== "none" && !row.querySelector('.no-data')
        );
        
        const tbody = document.querySelector(".modern-table tbody");
        const noResultsRow = document.getElementById("no-results-row");
        
        if (visibleRows.length === 0 && searchTerm !== "") {
            // Create "no results" row if it doesn't exist
            if (!noResultsRow) {
                const newRow = document.createElement("tr");
                newRow.id = "no-results-row";
                newRow.innerHTML = `
                    <td colspan="5" class="no-data">
                        <i class="uil uil-search"></i>
                        <span>No bookings found matching "${searchTerm}"</span>
                    </td>
                `;
                tbody.appendChild(newRow);
            } else {
                noResultsRow.style.display = "";
                noResultsRow.querySelector("span").textContent = `No bookings found matching "${searchTerm}"`;
            }
        } else if (noResultsRow) {
            noResultsRow.style.display = "none";
        }
    });
}

// Optional: Add smooth scrolling
document.addEventListener('DOMContentLoaded', function() {
    console.log('Miramar Hotel Dashboard initialized');
    
    // Animate numbers on page load
    const numbers = document.querySelectorAll('.box .number');
    numbers.forEach(numberEl => {
        const finalNumber = numberEl.textContent;
        // Skip if it's a percentage or has non-numeric characters
        if (finalNumber.includes('%') || finalNumber.includes('$')) {
            return;
        }
        
        const target = parseInt(finalNumber);
        if (!isNaN(target)) {
            animateNumber(numberEl, target);
        }
    });
});

// Animate number function
function animateNumber(element, target) {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 20);
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            if (!sidebar.classList.contains('close')) {
                sidebar.classList.add('close');
                localStorage.setItem("status", "close");
            }
        }
    }
});