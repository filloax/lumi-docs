addEventListener("load", (event) => {
    Array.from(document.getElementsByClassName('collapsible-button')).forEach(element => {
        element.addEventListener("click", event => {
            /** @type {HTMLElement} */
            const el = event.target
            let nextSibling = el.nextElementSibling;
        
            while (nextSibling) {
                if (nextSibling.classList.contains('collapsible')) {
                    break;
                }
                
                nextSibling = nextSibling.nextElementSibling;
            }
    
            el.classList.toggle("hidden")
            nextSibling.classList.toggle("hidden")
        });
    });
});
