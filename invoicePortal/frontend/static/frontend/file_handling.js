function chooseFiles() {
    const fileInput = document.getElementById('file-upload');

    // Disable directory selection
    fileInput.removeAttribute('webkitdirectory');
    fileInput.removeAttribute('mozdirectory');
    fileInput.removeAttribute('directory');

    fileInput.click();

    // Show the Upload button if files are selected
    fileInput.onchange = function() {
        if (fileInput.files.length > 0) {
            document.getElementById('uploadButton').style.display = 'inline';
        } else {
            document.getElementById('uploadButton').style.display = 'none';
        }
    };
}

function chooseFolder() {
    const fileInput = document.getElementById('file-upload');

    // Enable directory selection
    fileInput.setAttribute('webkitdirectory', '');
    fileInput.setAttribute('mozdirectory', '');
    fileInput.setAttribute('directory', '');

    fileInput.click();

    // Show the Upload button if a folder is selected
    fileInput.onchange = function() {
        if (fileInput.files.length > 0) {
            document.getElementById('uploadButton').style.display = 'inline';
        } else {
            document.getElementById('uploadButton').style.display = 'none';
        }
    };
}

function uploadFiles() {
    const fileInput = document.getElementById('file-upload');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const uploadNotification = document.getElementById('uploadNotification');
    const uploadButton = document.getElementById('uploadButton');
    const downloadButton = document.getElementById('downloadButton');

    loadingIndicator.style.display = 'block';
    uploadNotification.innerHTML = '';
    downloadButton.style.display = 'none'; // Hide the download button when uploading again

    if (fileInput.files && fileInput.files.length === 0) {
        alert('Please select one or more PDF files or a folder to upload.');
        return;
    }

    const formData = new FormData();
    const pdfFiles = [];
    const nonPdfFiles = [];
    // Append each file to the FormData object
    Array.from(fileInput.files).forEach((file, index) => {
        if (file.type === 'application/pdf') {
            formData.append('files', file);
            pdfFiles.push(file.name);
        } else {
            nonPdfFiles.push(file.name);
        }
    });

    let message = `${pdfFiles.length} PDF file(s) have been uploaded.`;
    if (nonPdfFiles.length > 0) {
        message += `<br>The following files were not uploaded because they are not PDF:`;
        nonPdfFiles.forEach(file => {
            message += `<br>${file}`;
        });
    }
    uploadNotification.innerHTML = message;

    // Disable the file input and upload button
    fileInput.disabled = true;
    uploadButton.disabled = true;

    $.ajax({
        url: '/api/upload/',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        xhr: function() {
            const xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        console.log('Upload success:', response);
                        if (response.task_ids && response.task_ids.length === 0) {
                            alert('No files uploaded.');
                            // Enable the file input and upload button if no files were uploaded
                            fileInput.disabled = false;
                            uploadButton.disabled = false;
                        } else {
                            const uploadId = response.upload_id;
                            // Start checking progress immediately after sending the upload request
                            checkUploadProgress(uploadId);
                        }
                    } else {
                        loadingIndicator.style.display = 'none';
                        console.error('Upload error:', xhr.statusText);
                        alert('Upload failed');
                        // Enable the file input and upload button on upload failure
                        fileInput.disabled = false;
                        uploadButton.disabled = false;
                    }
                }
            };
            return xhr;
        }
    });
}

function checkUploadProgress(uploadId) {
    const processedInvoicesElement = document.getElementById('processedInvoices');
    const pendingTasksElement = document.getElementById('pendingTasks');
    const downloadButton = document.getElementById('downloadButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const fileInput = document.getElementById('file-upload');
    const uploadButton = document.getElementById('uploadButton');
    let progressInterval;

    function getUploadProgress() {
        $.ajax({
            url: '/api/upload-progress/',
            method: 'GET',
            success: function(data) {
                const totalFiles = data.total_files;
                const processedFiles = data.processed_files;
                const completed = data.completed;

                processedInvoicesElement.textContent = processedFiles;
                pendingTasksElement.textContent = totalFiles - processedFiles;

                if (completed) {
                    clearInterval(progressInterval);
                    downloadButton.style.display = 'block';
                    downloadButton.onclick = () => { downloadFile(uploadId); };
                    loadingIndicator.style.display = 'none'; // Hide the loading indicator when the download button shows up
                    // Enable the file input and upload button after processing is completed
                    fileInput.disabled = false;
                    uploadButton.disabled = false;
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('Failed to get upload progress');
                clearInterval(progressInterval);
                loadingIndicator.style.display = 'none'; // Hide the loading indicator on progress check failure
                // Enable the file input and upload button on progress check failure
                fileInput.disabled = false;
                uploadButton.disabled = false;
            }
        });
    }

    // Clear any existing progress interval
    clearInterval(progressInterval);

    // Start a new progress interval
    progressInterval = setInterval(getUploadProgress, 3000);
}

function downloadFile(upload_id) {
    window.location.href = `/api/download/${upload_id}`;
}