function scrollToTop(e) {
    window.scrollTo(0, 0);
}

function init() {
    document.getElementById("toTopButton").addEventListener("click", (e) => scrollToTop(e));
}

init();
