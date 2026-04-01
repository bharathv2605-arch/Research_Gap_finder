/**
 * main.js - Frontend JavaScript
 * Research Gap Finder
 * Handles file upload UI, form interactions, and dynamic elements.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ============================================================
    // Flash message auto-dismiss after 5 seconds
    // ============================================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(function () { alert.remove(); }, 300);
        }, 5000);
    });


    // ============================================================
    // File Upload Drag & Drop
    // ============================================================
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const uploadForm = document.getElementById('upload-form');

    if (uploadArea && fileInput) {
        // Click to open file browser
        uploadArea.addEventListener('click', function () {
            fileInput.click();
        });

        // Drag and drop events
        uploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function () {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            displaySelectedFiles(fileInput.files);
        });

        // When files are selected via browser
        fileInput.addEventListener('change', function () {
            displaySelectedFiles(fileInput.files);
        });
    }

    /**
     * Display selected file names in the UI
     */
    function displaySelectedFiles(files) {
        if (!fileList) return;
        fileList.innerHTML = '';

        if (files.length === 0) return;

        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            var item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML =
                '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">' +
                '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>' +
                '</svg>' +
                '<span>' + file.name + '</span>' +
                '<span style="color:#94a3b8;font-size:0.75rem;">(' + formatFileSize(file.size) + ')</span>';
            fileList.appendChild(item);
        }
    }

    /**
     * Format file size to human-readable form
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        var k = 1024;
        var sizes = ['Bytes', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }


    // ============================================================
    // Upload form submission with loading state
    // ============================================================
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            var files = fileInput ? fileInput.files : [];
            if (files.length === 0) {
                e.preventDefault();
                alert('Please select at least one file to upload.');
                return;
            }
            // Show loading spinner
            var spinner = document.getElementById('upload-spinner');
            if (spinner) spinner.classList.add('active');

            var submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="spinner-circle" style="width:18px;height:18px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:8px;"></span>' +
                    'Uploading...';
            }
        });
    }


    // ============================================================
    // Select All Checkbox (Dashboard)
    // ============================================================
    var selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function () {
            var checkboxes = document.querySelectorAll('.paper-checkbox');
            checkboxes.forEach(function (cb) {
                cb.checked = selectAll.checked;
            });
        });
    }


    // ============================================================
    // Analysis Form - Show loading spinner
    // ============================================================
    var analyzeForm = document.getElementById('analyze-form');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function (e) {
            var checked = document.querySelectorAll('.paper-checkbox:checked');
            if (checked.length === 0) {
                e.preventDefault();
                alert('Please select at least one paper to analyze.');
                return;
            }

            // Show spinner
            var spinner = document.getElementById('analyze-spinner');
            if (spinner) spinner.classList.add('active');

            var submitBtn = analyzeForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="spinner-circle" style="width:18px;height:18px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:8px;"></span>' +
                    'Analyzing papers... This may take a moment';
            }
        });
    }


    // ============================================================
    // Smooth scroll for result sections
    // ============================================================
    var sectionLinks = document.querySelectorAll('.section-link');
    sectionLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

});
