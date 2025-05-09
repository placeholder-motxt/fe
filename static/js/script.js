document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileListSection = document.getElementById('fileListSection');
    const convertBtn = document.getElementById('convertButton');
    const csrftoken = getCookie('csrftoken');

    let uploadedFiles = [];
    let classFileCount = 0;

    // Initialize event listeners
    initializeEventListeners();

    function initializeEventListeners() {
        fileListSection.addEventListener('click', handleFileListClick);
        fileInput.addEventListener('change', handleFileInput);
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('dragleave', handleDragLeave);
        dropZone.addEventListener('drop', handleDrop);
        convertBtn.addEventListener('click', handleConvert);
    }

    // File management functions
    function handleFileListClick(e) {
        if (e.target.classList.contains('delete-btn')) {
            const filename = e.target.closest('.file-entry').dataset.filename;
            uploadedFiles = uploadedFiles.filter(file => file.name !== filename);
            updateFileList();
        }
    }

    function handleFileInput(e) {
        processFiles(Array.from(e.target.files));
        e.target.value = '';
    }

    function handleDrop(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        processFiles(Array.from(e.dataTransfer.files));
        fileInput.value = '';
    }

    function handleDragOver(e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }

    function handleDragLeave() {
        dropZone.classList.remove('dragover');
    }

    // Core file processing
    function processFiles(files) {
        files.forEach(file => {
            const validationMessage = validateFile(file);
            if (validationMessage) {
                showNotification(validationMessage, 'error');
                return;
            }
            uploadedFiles.push(file);
        });
        updateFileList();
    }

    function validateFile(file) {
        const isClass = file.name.toLowerCase().endsWith('.class.jet');
        const isSequence = file.name.toLowerCase().endsWith('.sequence.jet');
        
        if (!isClass && !isSequence) {
            return `Invalid file type: ${file.name}. Only .class.jet and .sequence.jet allowed`;
        }

        if (isClass) {
            classFileCount++;
            if (classFileCount > 1) {
                classFileCount--;
                return 'Only one .class.jet file is allowed!';
            }
        }

        return null;
    }

    function updateFileList() {
        fileListSection.innerHTML = '';
        classFileCount = 0;

        uploadedFiles.forEach(file => {
            if (file.name.toLowerCase().endsWith('.class.jet')) classFileCount++;
            fileListSection.appendChild(createFileElement(file));
        });

        toggleConvertButton();
    }

    function createFileElement(file) {
        const fileEntry = document.createElement('div');
        fileEntry.className = 'file-entry flex items-center justify-between bg-[var(--hover-tile)] rounded-lg p-4';
        fileEntry.innerHTML = `
            <div class="flex items-center space-x-2">
                <svg class="file-icon" viewBox="0 0 24 24">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-7-7zm0 18H6V4h7v16zm3-8h-2v2h-2v-2H9v-2h2V8h2v2h2v2zm2-10H5v16h14V4z"/>
                </svg>
                <span class="font-semibold text-[var(--secondary)]">${file.name}</span>
            </div>
            <button class="delete-btn">×</button>
        `;
        fileEntry.dataset.filename = file.name;
        return fileEntry;
    }

    function toggleConvertButton() {
        const hasFiles = uploadedFiles.length > 0;
        fileListSection.classList.toggle('hidden', !hasFiles);
        convertBtn.classList.toggle('hidden', !hasFiles);
    }

    // Conversion handling
    async function handleConvert() {
        if (uploadedFiles.length === 0) {
            showNotification('Please select files to convert.', 'error');
            return;
        }
    
        const formData = new FormData();
        uploadedFiles.forEach(file => formData.append('files', file));
    
        try {
            const response = await fetch('/convert_page/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                body: formData,
                credentials: 'same-origin',
            });
    
            if (response.ok) {
                const contentType = response.headers.get('content-type') || '';
                
                // Check if response is ZIP file
                if (contentType.includes('application/zip')) {
                    handleSuccessfulConversion(response);
                } else {
                    // Handle unexpected content type
                    const errorText = await response.text();
                    showNotification(`Error: Invalid response format - ${errorText}`, 'error');
                }
            } else {
                handleErrorResponse(response);
            }
        } catch (error) {
            showNotification('Network error - Check your connection', 'error');
            console.error('Error:', error);
        }
    }

    async function handleSuccessfulConversion(response) {
        try {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${uploadedFiles[0].name}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Files converted and downloaded successfully!', 'success');
        } catch (error) {
            showNotification('Error processing downloaded file', 'error');
            console.error('Download error:', error);
        }
    }

    async function handleErrorResponse(response) {
        const contentType = response.headers.get('content-type') || '';
        let message = 'Conversion failed';
    
        if (contentType.includes('application/json')) {
            const errorData = await response.json();
            
            // Handle FastAPI's 422 error structure
            if (errorData.detail && Array.isArray(errorData.detail)) {
                message = errorData.detail.map(err => err.msg).join('; ');
            } else {
                message = errorData.error || errorData.detail || message;
            }
        } else {
            message = await response.text();
        }
    
        showNotification(`Error ${response.status}: ${message}`, 'error');
    }

    // Notification system
    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const messageElement = document.getElementById('notificationMessage');
        
        messageElement.textContent = message;
        notification.className = `
            fixed top-4 right-4 max-w-md p-4 rounded-lg shadow-lg 
            ${type === 'error' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}
            transition-all
        `;
        
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 5000);
    }

    // Utility functions
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    handleDarkMode();
});
function handleDarkMode() {
    const themeToggle = document.getElementById("switch");
    const htmlElement = document.documentElement;

    // Load stored theme
    if (localStorage.getItem("theme") === "dark") {
        htmlElement.setAttribute("data-theme", "dark");
        themeToggle.checked = true;
    }
    else if (localStorage.getItem("theme") === "light") {
        htmlElement.setAttribute("data-theme", "light");
        themeToggle.checked = false;
    }

    // Toggle theme
    themeToggle.addEventListener("change", function () {
        if (themeToggle.checked) {
            htmlElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
        } else {
            htmlElement.setAttribute("data-theme", "light");
            localStorage.setItem("theme", "light");
            htmlElement.classList.remove("dark");
            
        }
    });

}
