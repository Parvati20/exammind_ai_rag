document.addEventListener('DOMContentLoaded', () => {
    // 1. Load History on page start
    displayHistory();

    // 2. Form submission logic
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function() {
            const query = document.getElementById('queryInput').value;
            const btn = document.querySelector('button[type="submit"]');

            // Save to LocalStorage
            saveSearchToHistory(query);

            // Loading Animation
            if (btn) {
                btn.innerHTML = 'Processing...';
                btn.disabled = true;
                btn.style.opacity = '0.7';
            }
        });
    }
});

function saveSearchToHistory(query) {
    if (query && query.trim() !== "") {
        let history = JSON.parse(localStorage.getItem('examHistory')) || [];
        history = history.filter(item => item !== query); // Remove duplicates
        history.unshift(query); 
        if (history.length > 5) history.pop(); // Keep only top 5
        localStorage.setItem('examHistory', JSON.stringify(history));
    }
}

function displayHistory() {
    const historyDiv = document.querySelector('.history-section');
    if (!historyDiv) return;

    let history = JSON.parse(localStorage.getItem('examHistory')) || [];
    let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <p style="color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin: 0;">Intelligence History</p>
            ${history.length > 0 ? '<button onclick="clearAllHistory()" style="background:none; border:none; color:#ef4444; font-size:0.7rem; cursor:pointer;">Clear</button>' : ''}
        </div>
    `;

    if (history.length > 0) {
        history.forEach(item => {
            html += `<div class="history-item" onclick="quickSearch('${item}')" style="cursor:pointer; margin-bottom:10px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px;">${item}</div>`;
        });
    } else {
        html += '<div style="color:gray; font-size:0.8rem;">No recent history</div>';
    }
    historyDiv.innerHTML = html;
}

function clearAllHistory() {
    if(confirm("Clear your search history?")) {
        localStorage.removeItem('examHistory');
        displayHistory();
    }
}

function quickSearch(text) {
    const input = document.getElementById('queryInput');
    const form = document.getElementById('searchForm');
    if (input && form) {
        input.value = text;
        form.submit();
    }
}