document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('fileInput');
  const dropzone = document.getElementById('dropzone');
  const previewContainer = document.getElementById('previewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const removeBtn = document.getElementById('removeBtn');
  const extractBtn = document.getElementById('extractBtn');
  const emptyState = document.getElementById('emptyState');
  const loadingState = document.getElementById('loadingState');
  const jsonResult = document.getElementById('jsonResult');
  const copyBtn = document.getElementById('copyBtn');
  const historyList = document.getElementById('historyList');
  const refreshBtn = document.getElementById('refreshBtn');

  const API_BASE_URL = 'http://localhost:8000/api/v1'; // Default local address
  let selectedFile = null;

  // Handle Drag & Drop events
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('border-indigo-500', 'bg-indigo-950/20');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('border-indigo-500', 'bg-indigo-950/20');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
      handleFileSelect(files[0]);
    }
  });

  // Handle Input select
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      handleFileSelect(e.target.files[0]);
    }
  });

  function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file.');
      return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      dropzone.classList.add('hidden');
      previewContainer.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  }

  // Remove file action
  removeBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    dropzone.classList.remove('hidden');
    previewContainer.classList.add('hidden');
    resetOutput();
  });

  function resetOutput() {
    emptyState.classList.remove('hidden');
    loadingState.classList.add('hidden');
    jsonResult.classList.add('hidden');
    copyBtn.classList.add('hidden');
  }

  // Call Extract API
  extractBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    emptyState.classList.add('hidden');
    loadingState.classList.remove('hidden');
    jsonResult.classList.add('hidden');
    copyBtn.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server returned code ${response.status}`);
      }

      const result = await response.json();
      loadingState.classList.add('hidden');

      if (result.success) {
        jsonResult.textContent = JSON.stringify(result.data, null, 2);
        jsonResult.classList.remove('hidden');
        copyBtn.classList.remove('hidden');
        loadHistory(); // Reload history after extraction
      } else {
        throw new Error(result.error || 'Failed to extract data.');
      }

    } catch (error) {
      loadingState.classList.add('hidden');
      jsonResult.textContent = `Error: ${error.message}`;
      jsonResult.classList.remove('hidden');
    }
  });

  // Copy JSON action
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(jsonResult.textContent)
      .then(() => {
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
          copyBtn.textContent = originalText;
        }, 2000);
      });
  });

  // Load history list
  async function loadHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      if (!response.ok) throw new Error('Failed to fetch history');

      const result = await response.json();
      if (result.success && result.data && result.data.length > 0) {
        historyList.innerHTML = result.data.map(invoice => `
          <tr class="hover:bg-slate-800/40 transition-colors">
            <td class="py-3 px-4 font-mono text-xs text-indigo-400">${invoice.invoice_number || 'N/A'}</td>
            <td class="py-3 px-4 font-medium">${invoice.vendor_name || 'N/A'}</td>
            <td class="py-3 px-4 font-mono">$${invoice.total_amount !== null && invoice.total_amount !== undefined ? invoice.total_amount.toFixed(2) : '0.00'}</td>
            <td class="py-3 px-4 font-mono">$${invoice.tax_amount !== null && invoice.tax_amount !== undefined ? invoice.tax_amount.toFixed(2) : '0.00'}</td>
            <td class="py-3 px-4">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Completed
              </span>
            </td>
          </tr>
        `).join('');
      } else {
        historyList.innerHTML = `
          <tr>
            <td colspan="5" class="py-6 text-center text-slate-500">No records found.</td>
          </tr>
        `;
      }
    } catch (error) {
      historyList.innerHTML = `
        <tr>
          <td colspan="5" class="py-6 text-center text-rose-400">Error loading history: ${error.message}</td>
        </tr>
      `;
    }
  }

  refreshBtn.addEventListener('click', loadHistory);

  // Initial load
  loadHistory();
});
