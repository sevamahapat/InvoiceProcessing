function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    if (fileInput.files.length === 0 || fileInput.files[0].type !== 'application/pdf') {
        alert('Please select a PDF file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/api/upload/', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            if (!response.ok) throw new Error('Upload failed');
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            if (data.task_id) {
                // Update the download link with the task ID
                const downloadButton = document.getElementById('downloadButton');
                downloadButton.style.display = 'block'; // Show the download button
                downloadButton.onclick = () => { downloadFile(data.task_id); };
                alert('File uploaded successfully. Task ID: ' + data.task_id);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert(error.message);
        });
}

function downloadFile(taskId) {
    window.location.href = `/api/download/${taskId}`;
    // Adjust the URL to include the task ID returned by the upload API.
}