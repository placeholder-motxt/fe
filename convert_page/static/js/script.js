document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileListSection = document.getElementById('fileListSection');
    const convertBtn = document.getElementById('convertButton');
    const csrftoken = getCookie('csrftoken');  // Get CSRF token

    let uploadedFiles = [];
    let classFileCount = 0;

    function validateFile(file) {
        const isClass = file.name.toLowerCase().endsWith('.class.jet');
        const isSequence = file.name.toLowerCase().endsWith('.sequence.jet');
        
        if (!isClass && !isSequence) {
            alert(`Invalid file type: ${file.name}. Only .class.jet and .sequence.jet allowed`);
            return false;
        }

        // Check for multiple .class.jet files
        if (isClass && classFileCount >= 1) {
            alert('Only one .class.jet file is allowed!');
            return false;
        }

        return true;
    }

    function updateFileList() {
        fileListSection.innerHTML = '';
        classFileCount = 0;

        uploadedFiles.forEach((file, index) => {
            if (file.name.toLowerCase().endsWith('.class.jet')) {
                classFileCount++;
            }

            const fileEntry = document.createElement('div');
            fileEntry.className = 'flex items-center justify-between bg-[var(--hover-tile)] rounded-lg p-4';
            fileEntry.innerHTML = `
                <div class="flex items-center space-x-2">
                    <svg class="file-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-7-7zm0 18H6V4h7v16zm3-8h-2v2h-2v-2H9v-2h2V8h2v2h2v2zm2-10H5v16h14V4z"/>
                    </svg>
                    <span class="font-semibold text-[var(--secondary)]">${file.name}</span>
                </div>
                <button class="delete-btn">×</button>
            `;

            const deleteBtn = fileEntry.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => {
                uploadedFiles = uploadedFiles.filter((_, i) => i !== index);
                updateFileList();
            });

            fileListSection.appendChild(fileEntry);
        });

        // Toggle Convert button visibility
        if (uploadedFiles.length > 0) {
            fileListSection.classList.remove('hidden');
            convertBtn.classList.remove('hidden');
        } else {
            fileListSection.classList.add('hidden');
            convertBtn.classList.add('hidden');
        }
    }

    // Drag-and-drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
        fileInput.value = '';
    });

    // File input handler
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
        e.target.value = '';
    });

    function handleFiles(files) {
        files.forEach(file => {
            if (validateFile(file)) {
                uploadedFiles.push(file);
            }
        });
        updateFileList();
    }

    // Convert button to trigger ZIP download
    convertBtn.addEventListener('click', async () => {
        if (uploadedFiles.length === 0) {
            alert('Please select files to convert.');
            return;
        }

        const formData = new FormData();
        uploadedFiles.forEach(file => formData.append('files', file));

        try {
            const response = await fetch('/convert_page/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken, 
                },
                body: formData,
                credentials: 'same-origin',
            });

            if (response.ok) {
                // Handle ZIP download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${uploadedFiles[0].name}.zip`;  // Use first filename for ZIP
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                alert('Files converted and downloaded successfully!');
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            alert('An error occurred while converting files.');
            console.error('Error:', error);
        }
    });

    // CSRF token helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const trimmedCookie = cookie.trim();
                if (trimmedCookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(trimmedCookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});