/** @type {Array} */ 
var all_data;

addEventListener("load", (event) => {
    fetchData()
    // document.getElementById('nameFilter').addEventListener('input', filterEntries);
    document.getElementById('nameFilter').hidden = true
});

function fetchData() {
    const myHeaders = new Headers();
    // myHeaders.append('pragma', 'no-cache');
    // myHeaders.append('cache-control', 'no-cache');

    
    fetch(`/data`, {
        // cache: "no-store", 
        headers: myHeaders,
    })
        .then(response => { 
            // console.log(response); 
            return response.json() 
        })
        .then(data => {
            all_data = data
            renderData(data)
            // filterEntries()
            
            // Init after loading data
            initDataTables()
        });
}

function initDataTables() {
    $('#pokemonTable').DataTable({
        paging: false,
        searching: true,
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
        let url = `/details/${entry['num']}/${entry['name']}`
        if ('form' in entry || 'region' in entry) {
            url += `/${entry['form'] || entry['region']}`
        }
        row.innerHTML = `
            <td>${ entry['num'] }</td>
            <td><a href="${url}">${ entry['name'] }${ regionSuffix }${formSuffix}</a></td>
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
    const value = stat["value"]
    if ("original" in stat) {
        const original = stat["original"]
        const changed_by = stat["changed_by"]
        const cls = "stat-from-" + changed_by
        const greater = value > original
        return `<td class="number"><span class="tooltip ${cls} ${greater ? "stat-buff" : "stat-nerf"}" title="${stat["original"]}">${value}</span></td>`
    } else {
        return `<td class="number">${value}</td>`
    }
}

function renderType(entry) {
    const typeData = entry["type"]
    const hasNotes = "type_notes" in entry
    /** @type {Array} */
    const changed_which = typeData["changed_which"] || []
    const notesAddon = hasNotes ? `<sup class="tooltip" title="${entry["type_notes"]}">note</sup>` : ''

    out = ''

    for (let i = 0; i < 2; i++) {
        const value = typeData['value'][i]
        const cls = changed_which.includes(i) ? `type-from-${typeData['source']}` : ''
        const cell_cls = value ? ` type-${value.toLowerCase()}` : ''
        out += `<td class="${cell_cls}"><span class="${cls}">${ value || '' }</span>${i == 1 ? notesAddon : ''}</td>\n`
    }

    return out
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
        out += `<sup class="tooltip" title="${abilityNotes}">note</sup>`;
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