document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const errorAlert = document.getElementById('errorAlert');
  const errorMessage = document.getElementById('errorMessage');
  const closeErrorBtn = document.getElementById('closeErrorBtn');

  const uploadContainer = document.getElementById('uploadContainer');
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const previewContainer = document.getElementById('previewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const previewFilename = document.getElementById('previewFilename');
  const previewFilesize = document.getElementById('previewFilesize');
  const removeBtn = document.getElementById('removeBtn');
  const extractBtn = document.getElementById('extractBtn');

  const loadingContainer = document.getElementById('loadingContainer');

  const resultContainer = document.getElementById('resultContainer');
  const resultFilename = document.getElementById('resultFilename');
  const confidenceBadge = document.getElementById('confidenceBadge');
  const processingTimeBadge = document.getElementById('processingTimeBadge');
  const resultImagePreview = document.getElementById('resultImagePreview');
  const jsonResult = document.getElementById('jsonResult');
  const copyBtn = document.getElementById('copyBtn');
  const copyBtnText = document.getElementById('copyBtnText');
  const tryAnotherBtn = document.getElementById('tryAnotherBtn');
  const downloadBtn = document.getElementById('downloadBtn');

  const historyList = document.getElementById('historyList');
  const refreshBtn = document.getElementById('refreshBtn');

  // Detail Modal Elements
  const detailModal = document.getElementById('detailModal');
  const modalBackdrop = document.getElementById('modalBackdrop');
  const modalTitle = document.getElementById('modalTitle');
  const modalSubtitle = document.getElementById('modalSubtitle');
  const modalJson = document.getElementById('modalJson');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalDownloadBtn = document.getElementById('modalDownloadBtn');

  // API configuration
  const API_BASE_URL = window.location.origin && window.location.origin.startsWith('http')
    ? '/api/v1'
    : 'http://localhost:8000/api/v1';

  // Application State
  let selectedFile = null;
  let currentExtractionData = null;
  let historyRecords = [];
  let currentModalRecord = null;

  // --- DRAG & DROP EVENTS ---
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('border-indigo-500', 'bg-indigo-950/10');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('border-indigo-500', 'bg-indigo-950/10');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
      onFileSelected(files[0]);
    }
  });

  dropzone.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      onFileSelected(e.target.files[0]);
    }
  });

  // --- FILE SELECT HANDLER ---
  function onFileSelected(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      showError('Unsupported file type. Please upload a JPEG, PNG, or WEBP image.');
      return;
    }
    
    // File size limit: 10MB
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      showError('File is too large. Maximum size is 10MB.');
      return;
    }

    selectedFile = file;
    hideError();

    // Show thumbnail preview
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      dropzone.classList.add('hidden');
      previewContainer.classList.remove('hidden');
      previewFilename.textContent = file.name;
      previewFilesize.textContent = formatBytes(file.size);
    };
    reader.readAsDataURL(file);
  }

  // --- REMOVE FILE BUTTON ---
  removeBtn.addEventListener('click', () => {
    resetUploadState();
  });

  function resetUploadState() {
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    dropzone.classList.remove('hidden');
    previewContainer.classList.add('hidden');
  }

  // --- EXTRACT BUTTON EVENT ---
  extractBtn.addEventListener('click', () => {
    if (selectedFile) {
      handleUpload(selectedFile);
    }
  });

  // --- UPLOAD HANDLER ---
  async function handleUpload(file) {
    // Show spinner, hide preview and errors
    previewContainer.classList.add('hidden');
    loadingContainer.classList.remove('hidden');
    hideError();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errMessage = `Error ${response.status}`;
        try {
          const errData = await response.json();
          errMessage = errData.error || errData.detail || errMessage;
        } catch (_) {}
        throw new Error(errMessage);
      }

      const result = await response.json();
      loadingContainer.classList.add('hidden');

      if (result.success) {
        currentExtractionData = result.data;
        renderResult(result.data, result.processing_time_ms);
        renderHistory(); // Refresh history table
      } else {
        throw new Error(result.error || 'Failed to extract invoice data.');
      }

    } catch (error) {
      loadingContainer.classList.add('hidden');
      // Show upload zone back so they can retry
      previewContainer.classList.remove('hidden');
      showError(`Extraction failed: ${error.message}`);
    }
  }

  // --- RESULT RENDERING ---
  function renderResult(data, processingTimeMs) {
    // Hide upload zone and loading, show result container
    uploadContainer.classList.add('hidden');
    resultContainer.classList.remove('hidden');

    // Populate filename & processing time
    resultFilename.textContent = selectedFile ? selectedFile.name : 'invoice.json';
    processingTimeBadge.textContent = `${Math.round(processingTimeMs)} ms`;

    // Set preview image to match selected file
    resultImagePreview.src = imagePreview.src;

    // Handle Confidence badge
    const conf = data.confidence_score !== undefined ? data.confidence_score : 1.0;
    confidenceBadge.textContent = `Confidence: ${(conf * 100).toFixed(0)}%`;
    confidenceBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ' + getConfidenceBadgeClass(conf);

    // Apply JSON formatting and syntax highlighting
    jsonResult.innerHTML = syntaxHighlight(data);
  }

  // --- HISTORY LOADING ---
  async function renderHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/history?limit=10`);
      if (!response.ok) {
        throw new Error(`Failed to load history list (${response.status})`);
      }

      const result = await response.json();
      if (result.success) {
        historyRecords = result.data || [];
        
        if (historyRecords.length === 0) {
          historyList.innerHTML = `
            <tr>
              <td colspan="5" class="py-10 text-center text-slate-500">No recent extractions found.</td>
            </tr>
          `;
          return;
        }

        historyList.innerHTML = historyRecords.map(item => {
          const total = item.total_amount !== null && item.total_amount !== undefined 
            ? Number(item.total_amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : '--';
          return `
            <tr data-id="${item.id}" class="hover:bg-indigo-950/20 cursor-pointer border-b border-slate-800/40 transition-colors">
              <td class="py-3.5 px-4 font-medium text-slate-200 truncate max-w-[150px]">${item.filename || 'invoice.png'}</td>
              <td class="py-3.5 px-4 text-slate-300 font-medium">${item.vendor || 'Unknown'}</td>
              <td class="py-3.5 px-4 font-mono text-slate-200 font-semibold">${total}</td>
              <td class="py-3.5 px-4 font-mono text-slate-400 text-xs">${item.currency || 'USD'}</td>
              <td class="py-3.5 px-4 text-slate-400 text-xs">${formatDateTime(item.created_at)}</td>
            </tr>
          `;
        }).join('');

        // Attach click listener for each row
        const rows = historyList.querySelectorAll('tr[data-id]');
        rows.forEach(row => {
          row.addEventListener('click', () => {
            const recordId = row.getAttribute('data-id');
            const record = historyRecords.find(r => r.id == recordId);
            if (record) {
              openDetailModal(record);
            }
          });
        });
      }
    } catch (error) {
      historyList.innerHTML = `
        <tr>
          <td colspan="5" class="py-10 text-center text-rose-400">Failed to load history: ${error.message}</td>
        </tr>
      `;
    }
  }

  // --- DOWNLOAD ACTION ---
  function downloadJSON(filename, data) {
    if (!data) return;
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'invoice_data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Connect download buttons
  downloadBtn.addEventListener('click', () => {
    if (currentExtractionData) {
      const baseFilename = selectedFile ? selectedFile.name.split('.').slice(0, -1).join('.') : 'invoice';
      downloadJSON(`${baseFilename}_extracted.json`, currentExtractionData);
    }
  });

  modalDownloadBtn.addEventListener('click', () => {
    if (currentModalRecord) {
      const baseFilename = currentModalRecord.filename 
        ? currentModalRecord.filename.split('.').slice(0, -1).join('.') 
        : 'invoice';
      const rawJson = currentModalRecord.raw_json || currentModalRecord;
      downloadJSON(`${baseFilename}_history.json`, rawJson);
    }
  });

  // --- TRY ANOTHER (RESET) BUTTON ---
  tryAnotherBtn.addEventListener('click', () => {
    resetUploadState();
    currentExtractionData = null;
    resultContainer.classList.add('hidden');
    uploadContainer.classList.remove('hidden');
    hideError();
  });

  // --- DETAIL MODAL WORKFLOW ---
  function openDetailModal(record) {
    currentModalRecord = record;
    modalTitle.textContent = record.vendor || 'Invoice Details';
    modalSubtitle.textContent = record.filename || 'raw_extraction.json';
    
    // We display raw_json if it exists, otherwise represent the flat record fields
    const displayJson = record.raw_json || record;
    modalJson.innerHTML = syntaxHighlight(displayJson);

    detailModal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  }

  function closeDetailModal() {
    detailModal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    currentModalRecord = null;
  }

  modalBackdrop.addEventListener('click', closeDetailModal);
  closeModalBtn.addEventListener('click', closeDetailModal);
  modalCloseBtn.addEventListener('click', closeDetailModal);

  // --- REFRESH BUTTON EVENT ---
  refreshBtn.addEventListener('click', () => {
    renderHistory();
  });

  // --- COPY JSON BUTTON ---
  copyBtn.addEventListener('click', () => {
    if (!currentExtractionData) return;
    const rawText = JSON.stringify(currentExtractionData, null, 2);
    navigator.clipboard.writeText(rawText).then(() => {
      copyBtnText.textContent = 'Copied!';
      setTimeout(() => {
        copyBtnText.textContent = 'Copy';
      }, 2000);
    });
  });

  // --- ERROR BOX WORKFLOW ---
  function showError(message) {
    errorMessage.textContent = message;
    errorAlert.classList.remove('hidden');
    // Scroll error into view
    errorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function hideError() {
    errorAlert.classList.add('hidden');
    errorMessage.textContent = '';
  }

  closeErrorBtn.addEventListener('click', hideError);

  // --- HELPER FUNCTIONS ---
  function getConfidenceBadgeClass(score) {
    if (score > 0.8) {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    } else if (score > 0.5) {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    } else {
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    }
  }

  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  function formatDateTime(dateStr) {
    if (!dateStr) return '--';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateStr;
    }
  }

  function syntaxHighlight(json) {
    if (typeof json !== 'string') {
      json = JSON.stringify(json, null, 2);
    }
    // Escape HTML characters
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // Matches keys, strings, numbers, booleans, and nulls
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function (match) {
      let cls = 'text-amber-400'; // Default class: number
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'text-indigo-400 font-semibold'; // Key
        } else {
          cls = 'text-emerald-400'; // String value
        }
      } else if (/true|false/.test(match)) {
        cls = 'text-purple-400 font-medium'; // Boolean value
      } else if (/null/.test(match)) {
        cls = 'text-slate-500 italic'; // Null value
      }
      
      if (cls.includes('text-indigo-400')) {
        return `<span class="${cls}">${match.slice(0, -1)}</span>:`;
      }
      return `<span class="${cls}">${match}</span>`;
    });
  }

  // --- INITIAL LOAD ---
  renderHistory();
});
