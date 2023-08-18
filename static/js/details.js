addEventListener("load", (event) => {
    document.querySelectorAll(".move").forEach(el => {
        const move = el.textContent
        const link = `https://bulbapedia.bulbagarden.net/wiki/${move.replace(" ", "_")}_(move)`
        el.innerHTML = `<a href="${link}">${move}</a>`
    });
});