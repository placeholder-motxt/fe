document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileListSection = document.getElementById('fileListSection');
    const convertBtn = document.getElementById('convertButton');

    let uploadedFiles = []; // Menyimpan semua file yang valid
    let classFileCount = 0; // Counter untuk .class.jet

    function validateFile(file) {
        const isClass = file.name.toLowerCase().endsWith('.class.jet');
        const isSequence = file.name.toLowerCase().endsWith('.sequence.jet');
        
        if (!isClass && !isSequence) {
            alert(`Invalid file type: ${file.name}. Only .class.jet and .sequence.jet allowed`);
            return false;
        }

        // Validasi hanya 1 file .class.jet
        if (isClass && classFileCount >= 1) {
            alert('Only one .class.jet file is allowed!');
            return false;
        }

        return true;
    }

    function updateFileList() {
        fileListSection.innerHTML = '';
        classFileCount = 0; // Reset counter

        uploadedFiles.forEach((file, index) => {
            // Hitung jumlah .class.jet
            if (file.name.toLowerCase().endsWith('.class.jet')) {
                classFileCount++;
            }

            // Buat entry file
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

            // Event listener untuk hapus file
            const deleteBtn = fileEntry.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => {
                uploadedFiles = uploadedFiles.filter((_, i) => i !== index);
                updateFileList(); // Perbarui daftar setelah hapus
            });

            fileListSection.appendChild(fileEntry);
        });

        // Tampilkan/hide Convert button dan fileListSection
        if (uploadedFiles.length > 0) {
            fileListSection.classList.remove('hidden');
            convertBtn.classList.remove('hidden');
        } else {
            fileListSection.classList.add('hidden');
            convertBtn.classList.add('hidden');
        }
    }

    // Event listener untuk drag-and-drop
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
        fileInput.value = ''; // Reset input untuk mengizinkan upload file yang sama
    });

    // Event listener untuk file input
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
        e.target.value = ''; // Reset input setelah upload
    });

    function handleFiles(files) {
        files.forEach(file => {
            if (validateFile(file)) {
                uploadedFiles.push(file);
            }
        });
        updateFileList(); // Perbarui daftar file setelah upload
    }

    // Convert button untuk mengirim semua file
    convertBtn.addEventListener('click', async () => {  
        if (uploadedFiles.length === 0) {  
            alert('Please select files to convert.');  
            return;  
        }  
    
        // Check for duplicate filenames  
        const filenames = uploadedFiles.map(file => file.name);  
        if (new Set(filenames).size !== filenames.length) {  
            alert('Duplicate filenames are not allowed!');  
            return;  
        }  
    
        // Process files and collect data  
        const processedData = {  
            filename: filenames,  
            content: []  
        };  
    
        for (const file of uploadedFiles) {  
            try {  
                const text = await file.text();  
                const parsedContent = JSON.parse(text);  
                processedData.content.push([parsedContent]); // Wrap content in a list  
            } catch (error) {  
                alert(`Error parsing ${file.name}: ${error.message}`);  
                return;  
            }  
        }  
    
        // Display JSON in new window  
        const jsonBodyString = JSON.stringify(processedData, null, 2);  
        const popup = window.open('', '_blank');  
        popup.document.write(`  
            <html>  
                <head><title>JSON Preview</title></head>  
                <body>  
                    <pre>${jsonBodyString}</pre>  
                </body>  
            </html>  
        `);  
        popup.document.close();  
    });  

    // Fungsi untuk mengambil CSRF token
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