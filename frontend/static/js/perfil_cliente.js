document.addEventListener("DOMContentLoaded", () => {
    const layout = document.querySelector("[data-profile-layout]");
    const tabs = Array.from(document.querySelectorAll("[role='tab'][aria-controls]"));

    if (!layout || tabs.length === 0) {
        return;
    }

    const activateTab = (selectedTab, moveFocus = false) => {
        tabs.forEach((tab) => {
            const selected = tab === selectedTab;
            const panel = document.getElementById(tab.getAttribute("aria-controls"));

            tab.classList.toggle("is-active", selected);
            tab.setAttribute("aria-selected", String(selected));
            tab.setAttribute("tabindex", selected ? "0" : "-1");
            panel?.classList.toggle("is-active", selected);
        });

        if (moveFocus) {
            selectedTab.focus();
        }
    };

    layout.classList.add("perfil-tabs-ready");

    const tabFromHash = tabs.find((tab) => `#${tab.getAttribute("aria-controls")}` === window.location.hash);
    if (tabFromHash) {
        activateTab(tabFromHash);
    }

    tabs.forEach((tab, index) => {
        tab.addEventListener("click", (event) => {
            event.preventDefault();
            activateTab(tab);
        });

        tab.addEventListener("keydown", (event) => {
            let nextIndex = index;

            if (event.key === "ArrowRight") {
                nextIndex = (index + 1) % tabs.length;
            } else if (event.key === "ArrowLeft") {
                nextIndex = (index - 1 + tabs.length) % tabs.length;
            } else if (event.key === "Home") {
                nextIndex = 0;
            } else if (event.key === "End") {
                nextIndex = tabs.length - 1;
            } else {
                return;
            }

            event.preventDefault();
            activateTab(tabs[nextIndex], true);
        });
    });
});