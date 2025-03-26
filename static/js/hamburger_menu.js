function initHamburgerMenu() {
    const hamburgerButton = document.getElementById('hamburgerButton');
    const dropdownMenu = document.getElementById('dropdownMenu');
    
    if (!hamburgerButton || !dropdownMenu) {
        console.error('Hamburger menu elements not found');
        return;
    }
    
    // Toggle dropdown menu
    hamburgerButton.addEventListener('click', function(event) {
        event.stopPropagation();
        dropdownMenu.classList.toggle('active');
        hamburgerButton.classList.toggle('active');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!hamburgerButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('active');
            hamburgerButton.classList.remove('active');
        }
    });
    
    // Prevent clicks inside dropdown from closing it
    dropdownMenu.addEventListener('click', function(event) {
        // Only stop propagation if clicking on the menu itself, not its children links
        if (event.target === dropdownMenu) {
            event.stopPropagation();
        }
    });
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    initHamburgerMenu();
});

/* istanbul ignore next */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initHamburgerMenu };
}