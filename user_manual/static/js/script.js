document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll("nav > div > a");
    const mainContent = document.querySelector(".flex-1");
    const subMenus = document.querySelectorAll(".submenu");
    let current = "";
    
    mainContent.addEventListener("scroll", () => {
        const mainContentTop = mainContent.scrollTop;
        
        sections.forEach((section) => {
            const sectionTop = section.offsetTop - mainContentTop;
            console.log(current, sectionTop)

            if (sectionTop <= 100) { // Adjust threshold as needed
                if (section.getAttribute("id").includes("sub")){
                    return;
                } 
                current = section.getAttribute("id");
            }
        });
        
        navLinks.forEach((link) => {
            link.classList.remove("bg-teal-200", "text-black");
            link.classList.add("bg-white");
            if (current!="" && link.getAttribute("href").includes(current)) {
                link.classList.remove("bg-white");
                link.classList.add("bg-teal-200", "text-black");
                // Expand the corresponding submenu
                const submenu = link.nextElementSibling;
                if (submenu && submenu.classList.contains("submenu")) {
                    submenu.classList.remove("hidden");
                }
            } else {
                // Collapse all other submenus
                const submenu = link.nextElementSibling;
                if (submenu && submenu.classList.contains("submenu")) {
                    submenu.classList.add("hidden");
                }
            }
        });
    });
});