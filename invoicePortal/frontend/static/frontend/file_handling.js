function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.style.display = 'block';
    if (fileInput.files && fileInput.files.length === 0) {
        alert('Please select one or more PDF files to upload.');
        return;
    }

    const formData = new FormData();
    // Append each file to the FormData object
    Array.from(fileInput.files).forEach((file, index) => {
        if (file.type !== 'application/pdf') {
            alert('Only PDF files are allowed.');
            return;
        }
        formData.append('files', file);
        console.log(`File ${index + 1}: ${file.name}`);
    });

    fetch('/api/upload/', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            if (!response.ok) throw new Error('Upload failed');
            loadingIndicator.style.display = 'none';
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            if (data.task_ids && data.task_ids.length === 0) {
                alert('No files uploaded.');
                loadingIndicator.style.display = 'none';
                return;
            } else {
                const downloadButton = document.getElementById('downloadButton');
                downloadButton.style.display = 'block'; // Show the download button
                downloadButton.onclick = () => { downloadFile(data.upload_id); };
                alert('File processed successfully.');
                loadingIndicator.style.display = 'none';
            }
        })
        .catch((error) => {
            loadingIndicator.style.display = 'none';
            console.error('Error:', error);
            alert(error.message);
        });
}

function downloadFile(upload_id) {
    window.location.href = `/api/download/${upload_id}`;
    // Adjust the URL to include the task ID returned by the upload API.
}