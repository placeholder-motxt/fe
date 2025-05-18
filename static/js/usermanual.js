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

// Sidebar collapse for mobile/tablet
        const sidebar = document.getElementById('sidebar');
        const collapseBtn = document.getElementById('sidebarCollapseBtn');
        const sidebarToggle = document.getElementById('sidebarToggle');
        function closeSidebar() {
            sidebar.style.transform = 'translateX(-100%)';
            collapseBtn.style.display = 'flex';
        }
        function openSidebar() {
            sidebar.style.transform = 'translateX(0)';
            collapseBtn.style.display = 'none';
        }
        // Hide sidebar on small screens by default
        function handleResize() {
            if (window.innerWidth < 1280) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }
        window.addEventListener('resize', handleResize);
        document.addEventListener('DOMContentLoaded', () => {
            handleResize();
            if (sidebarToggle) {
                sidebarToggle.addEventListener('click', () => closeSidebar());
            }
            if (collapseBtn) {
                collapseBtn.addEventListener('click', () => openSidebar());
            }
        });

        // Collapsible submenu logic
        function toggleSubmenu(id, event) {
            event.preventDefault();
            const submenu = document.getElementById(id);
            if (submenu) {
                submenu.classList.toggle('hidden');
            }
        }