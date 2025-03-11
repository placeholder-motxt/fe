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
                // if (section.getAttribute("id")?.includes("sub")){
                //     return
                // }
                current = section.getAttribute("id");
                console.log(current)
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove("bg-[#4BDEC3]", "text-black");
            link.classList.add("bg-white");

            if (current !== "" && link.getAttribute("href").slice(1)===current) {
                link.classList.remove("bg-white");
                link.classList.add("bg-[#4BDEC3]", "text-black");
                
                
                // Expand the corresponding submenu
                const parent = link.parentElement;
                if (link.getAttribute("href").slice(1)===current&&
                    parent.classList.contains("submenu")) {
                    parent.classList.remove("hidden");
                    lastActiveParent = parent; // Save the last active submenu
                }
                
            }
        });
        
        
        // Collapse submenus if their parent is not active, but keep it open if:
        // 1. `current` is a sub-section, OR
        // 2. `lastActiveParent` was previously open (allows reopening when scrolling back)
        document.querySelectorAll(".submenu").forEach((submenu) => {

            submenu.classList.add("hidden");
            if (current.includes(submenu.getAttribute("id")?.slice(0,4))) {
                console.log(submenu)
                submenu.classList.remove("hidden");
            }
        });
        
    });
});