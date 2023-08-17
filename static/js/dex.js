/** @type {Array} */ 
var all_data;

addEventListener("load", (event) => {
    fetchData()
    document.getElementById('nameFilter').addEventListener('input', filterEntries);
});

function fetchData() {
    const myHeaders = new Headers();
    myHeaders.append('pragma', 'no-cache');
    myHeaders.append('cache-control', 'no-cache');

    
    fetch(`/data`, {cache: "no-store", headers: myHeaders})
        .then(response => { 
            // console.log(response); 
            return response.json() 
        })
        .then(data => {
            all_data = data
            renderData(data)
            filterEntries()
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
        row.attributes['data-entry'] = entry
        /** @type {Array} */
        const stats = entry["stats"]
        if (!("stats" in entry)) {
            console.log(entry)
        }
        const statPart = STATS.map((s) => renderStat(stats[s]) ).join("\n")
        const regionSuffix = (entry['region']) ? `-${entry['region']}` : ''
        "".toC
        const formSuffix = (entry['form']) ? ` (${titleCase(entry['form'])})` : ''
        row.innerHTML = `
            <td>${ entry['num'] }${ regionSuffix }</td>
            <td>${ entry['name'] }${ regionSuffix }${formSuffix}</td>
            ${ renderType(entry) }
            ${ renderAbilities(entry) }
            ${statPart}
        `;
        entryList.appendChild(row);
    });
}

function filterEntries() {
    const filter = document.getElementById('nameFilter').value.toLowerCase()
    const filteredData = all_data.filter(entry => entry["name"].toLowerCase().includes(filter) || entry["num"].toString().includes(filter))
    renderData(filteredData)
}

function renderStat(stat) {
    return `<td>${stat["value"]}</td>`
}

function renderType(entry) {
    const typeData = entry["type"]
    const hasNotes = "type_notes" in entry
    const is_changed = 'source' in typeData
    const cls = is_changed ? `type-from-${typeData['source']}` : ""
    /** @type {Array} */
    const changed_which = typeData["changed_which"] || []
    const cls0 = changed_which.includes(0) ? cls : ''
    const cls1 = changed_which.includes(1) ? cls : ''
    const notesAddon = hasNotes ? `<span class="tooltip" title="${entry["type_notes"]}">*</span>` : ''
    return `<td><span class="${cls0}">${ typeData['value'][0] }</span></td>
            <td><span class="${cls1}">${ typeData['value'][1] || '' }</span>${notesAddon}</td>
            `
}

function renderAbilities(entry) {
    const abilities = entry["abilities"];
    const hasNotes = "ability_notes" in entry;
    let out = "<td>";
    out += abilities.map(ability => {
        const cls = ("source" in ability) ? `ab-from-${ability["source"]}` : "";
        const val = ability['value'];
        const bulbapedia_link = `https://bulbapedia.bulbagarden.net/wiki/${val.replace(" ", "_")}_(Ability)`;
        return `<span class="${cls}"><a href="${bulbapedia_link}">${val}</a></span>`;
    }).join(", ");
    if (hasNotes) {
        const abilityNotes = entry["ability_notes"];
        out += `<span class="tooltip" title="${abilityNotes}">*</span>`;
    }
    out += "</td>";
    return out;
}

function titleCase(str) {
    str = str.toLowerCase().split(' ');
    for (var i = 0; i < str.length; i++) {
      str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1); 
    }
    return str.join(' ');
  }