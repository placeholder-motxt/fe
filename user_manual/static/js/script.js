document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll("nav a");
    const mainContent = document.querySelector(".flex-1");
    let current = "";
    let lastActiveParent = null; // Store the last active parent menu

    mainContent.addEventListener("scroll", () => {
        const mainContentTop = mainContent.scrollTop;

        sections.forEach((section) => {
            const sectionTop = section.offsetTop - mainContentTop;

            if (sectionTop <= 50) { // Adjust threshold as needed
                current = section.getAttribute("id");
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove("bg-[#4BDEC3]", "text-black");
            link.classList.add("bg-white");

            if (current !== "" && link.getAttribute("href")?.includes(current)) {
                link.classList.remove("bg-white");
                link.classList.add("bg-[#4BDEC3]", "text-black");

                // Expand the corresponding submenu
                const submenu = link.nextElementSibling;
                if (submenu?.classList.contains("submenu")) {
                    submenu.classList.remove("hidden");
                    lastActiveParent = submenu; // Save the last active submenu
                }
            }
        });

        // Collapse submenus if their parent is not active, but keep it open if:
        // 1. `current` is a sub-section, OR
        // 2. `lastActiveParent` was previously open (allows reopening when scrolling back)
        document.querySelectorAll(".submenu").forEach((submenu) => {
            const parentLink = submenu.previousElementSibling;

            if (
                parentLink &&
                !parentLink.getAttribute("href")?.includes(current) &&
                !current.includes("sub")
            ) {
                submenu.classList.add("hidden");
            } else if (submenu === lastActiveParent) {
                submenu.classList.remove("hidden"); // Reopen the last active submenu when scrolling back
            }
        });
    });
});
