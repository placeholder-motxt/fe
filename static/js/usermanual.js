document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll("nav a");
    const mainContent = document.getElementById("mainContent");
    const sidebar = document.getElementById('sidebar');
    const collapseBtn = document.getElementById('sidebarCollapseBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    let current = "";

    mainContent.addEventListener("scroll", () => {
        const mainContentTop = mainContent.scrollTop;
        sections.forEach((section) => {
            const sectionTop = section.offsetTop - mainContentTop;
            if (sectionTop <= 50) {
                current = section.getAttribute("id");
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove("bg-[#4BDEC3]", "text-black");
            link.classList.add("bg-white");

            if (current !== "" && link.getAttribute("href").slice(1) === current) {
                link.classList.remove("bg-white");
                link.classList.add("bg-[#4BDEC3]", "text-black");

                const parent = link.parentElement;
                if (
                    link.getAttribute("href").slice(1) === current &&
                    parent.classList.contains("submenu")
                ) {
                    parent.classList.remove("hidden");
                }
            }
        });

        document.querySelectorAll(".submenu").forEach((submenu) => {
            submenu.classList.add("hidden");
            if (current.includes(submenu.getAttribute("id")?.slice(0, 4))) {
                submenu.classList.remove("hidden");
            }
        });
    });

    // Close submenu when not hovered
    document.querySelectorAll(".submenu").forEach((submenu) => {
        submenu.addEventListener("mouseenter", () => {
            submenu.classList.remove("hidden");
        });
        submenu.addEventListener("mouseleave", () => {
            submenu.classList.add("hidden");
        });
    });

    // Sidebar collapse for mobile/tablet
    console.log('sidebar', sidebar);
    function closeSidebar() {
        console.log('closeSidebar');
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