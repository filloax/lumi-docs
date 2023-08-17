/** @type {Array} */ 
var all_data;

addEventListener("load", (event) => {
    fetchData()
    document.getElementById('nameFilter').addEventListener('input', filterEntries);
    filterEntries()
});

function fetchData() {
    fetch(`/data`)
        .then(response => response.json())
        .then(data => {
            all_data = data
            renderData(data)
        });
}

const STATS = [
    "HP",
    "Atk",
    "Def",
    "SpA",
    "SpD",
    "Spe",
    "BST",
]

function renderData(data) {
    const entryList = document.getElementById('entryList');
    entryList.innerHTML = '';
    data.forEach(entry => {
        const row = document.createElement('tr');
        /** @type {Array} */
        const stats = entry["stats"]
        const statPart = STATS.map((s) => renderStat(stats[s]) ).join("\n")
        const regionPrefix = (entry['region']) ? `-${entry['region']}` : ''
        row.innerHTML = `
            <td>${ entry['num'] }${ regionPrefix }</td>
            <td>${ entry['name'] }${ regionPrefix }</td>
            <td>${ entry['type'][0] }</td>
            <td>${ entry['type'][1] || '' }</td>
            <td>${ entry['abilities'].join(', ') }</td>
            ${statPart}
        `;
        entryList.appendChild(row);
    });
}

function renderStat(stat) {
    return `<td>${stat["value"]}</td>`
}

function filterEntries() {
    const filter = document.getElementById('nameFilter').value.toLowerCase()
    const filteredData = all_data.filter(entry => entry["name"].toLowerCase().includes(filter) || entry["num"].toString().includes(filter))
    renderData(filteredData)
}