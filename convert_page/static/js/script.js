document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const deleteBtn = document.querySelector('.delete-btn');
    const convertBtn = document.getElementById('convertButton');

    function validateFile(file) {
        return file.name.toLowerCase().endsWith('.jet');
    }

    function updateDisplay(file) {
        const fileInfoSection = document.getElementById('fileInfoSection');
        if (!file) {
            fileInfoSection.classList.add('hidden');
            dropZone.style.display = 'block';
            return;
        }
        fileNameDisplay.textContent = file.name;
        fileInfoSection.classList.remove('hidden');
        dropZone.style.display = 'none';
    }

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
        const file = e.dataTransfer.files[0];
        if (!validateFile(file)) {
            alert('Only .JET files are allowed');
            return;
        }
        fileInput.files = e.dataTransfer.files;
        updateDisplay(file);
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && !validateFile(file)) {
            alert('Only .JET files are allowed');
            e.target.value = '';
            return;
        }
        updateDisplay(file);
    });

    deleteBtn.addEventListener('click', () => {
        fileInput.value = '';
        updateDisplay(null);
    });

    convertBtn.addEventListener('click', () => {
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file to convert.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/convert_page/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Uncomment when CSRF is enabled
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                const jsonBody = JSON.stringify(data.json_body, null, 2);
                const popup = window.open('', '_blank');
                popup.document.write(`
                    <html>
                        <head><title>Output</title></head>
                        <body>
                            <pre>${jsonBody}</pre>
                        </body>
                    </html>
                `);
                popup.document.close();
            }
        })
        .catch(error => alert('An error occurred.'));
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {  // Use `for-of` instead of `for`
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