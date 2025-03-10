document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileListSection = document.getElementById('fileListSection');
    const convertBtn = document.getElementById('convertButton');
    const csrftoken = getCookie('csrftoken');

    let uploadedFiles = [];
    let classFileCount = 0;

    // Event delegation for delete buttons
    fileListSection.addEventListener('click', handleFileListClick);

    // Initialize file input
    fileInput.addEventListener('change', handleFileInput);
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    convertBtn.addEventListener('click', handleConvert);

    function handleFileListClick(e) {
        if (e.target.classList.contains('delete-btn')) {
            const filename = e.target.closest('.file-entry').dataset.filename;
            uploadedFiles = uploadedFiles.filter(file => file.name !== filename);
            updateFileList();
        }
    }

    function handleFileInput(e) {
        const files = Array.from(e.target.files);
        processFiles(files);
        e.target.value = '';
    }

    function handleDrop(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        processFiles(files);
        fileInput.value = '';
    }

    function handleDragOver(e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }

    function handleDragLeave() {
        dropZone.classList.remove('dragover');
    }

    function processFiles(files) {
        files.forEach(file => {
            if (validateFile(file)) {
                uploadedFiles.push(file);
            }
        });
        updateFileList();
    }

    function validateFile(file) {
        const isClass = file.name.toLowerCase().endsWith('.class.jet');
        const isSequence = file.name.toLowerCase().endsWith('.sequence.jet');
        
        if (!isClass && !isSequence) {
            alert(`Invalid file type: ${file.name}. Only .class.jet and .sequence.jet allowed`);
            return false;
        }

        if (isClass) {
            classFileCount++;
            if (classFileCount > 1) {
                alert('Only one .class.jet file is allowed!');
                classFileCount--;
                return false;
            }
        }

        return true;
    }

    function updateFileList() {
        fileListSection.innerHTML = '';
        classFileCount = 0;  // Reset and recalculate

        uploadedFiles.forEach(file => {
            if (file.name.toLowerCase().endsWith('.class.jet')) {
                classFileCount++;
            }

            const fileEntry = createFileElement(file);
            fileListSection.appendChild(fileEntry);
        });

        toggleConvertButton();
    }

    function createFileElement(file) {
        const fileEntry = document.createElement('div');
        fileEntry.className = 'file-entry flex items-center justify-between bg-[var(--hover-tile)] rounded-lg p-4';
        fileEntry.innerHTML = `
            <div class="flex items-center space-x-2">
                <svg class="file-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-7-7zm0 18H6V4h7v16zm3-8h-2v2h-2v-2H9v-2h2V8h2v2h2v2zm2-10H5v16h14V4z"/>
                </svg>
                <span class="font-semibold text-[var(--secondary)]">${file.name}</span>
            </div>
            <button class="delete-btn">×</button>
        `;
        fileEntry.dataset.filename = file.name;  // Add filename as data attribute
        return fileEntry;
    }

    function toggleConvertButton() {
        const hasFiles = uploadedFiles.length > 0;
        fileListSection.classList.toggle('hidden', !hasFiles);
        convertBtn.classList.toggle('hidden', !hasFiles);
    }

    async function handleConvert() {
        if (uploadedFiles.length === 0) return alert('Please select files to convert.');

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
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${uploadedFiles[0].name}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                alert('Files converted and downloaded successfully!');
            } else {
                // Check if response is JSON
                const contentType = response.headers.get('content-type') || '';
                if (contentType.includes('application/json')) {
                    const errorData = await response.json();
                    const errorMessage = errorData.error || errorData.detail || 'Unknown error';
                    alert(`Error Code: ${response.status}\nMessage: ${errorMessage}`);
                } else {
                    // Fallback for non-JSON errors (e.g., HTML error pages)
                    const errorText = await response.text();
                    alert(`Error Code: ${response.status}\nMessage: ${errorText}`);
                }
            }
        } catch (error) {
            // Handle network-level errors
            alert('A critical error occurred. Check your connection and try again.');
            console.error('Error:', error);
        }
    }

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
});