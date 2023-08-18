addEventListener("load", (event) => {
    document.querySelectorAll(".move").forEach(el => {
        const move = el.textContent
        const link = `https://bulbapedia.bulbagarden.net/wiki/${move.replace(" ", "_")}_(move)`
        el.innerHTML = `<a href="${link}">${move}</a>`
    });

    fixTypesFlexbox()

    const maxStat = 255
    const maxTotalStat = 780

    document.querySelectorAll(".statbar").forEach(el => {
        const value = parseInt(el.dataset['value'])
        const stat = el.dataset['stat']
        const total = (stat === "BST") ? maxTotalStat : maxStat
        el.style.width = `${value * 255 / total}px`
    });
});

function fixTypesFlexbox() {
    document.querySelectorAll(".type-container.original").forEach(el => {
        el.style.width = `${el.clientWidth * 0.6}px` // match css scale
    });
}