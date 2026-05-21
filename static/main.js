// State management
let currentTab = 'aruco';
let debounceTimer = null;

// DOM Elements
const codePreview = document.getElementById('code-preview');
const previewPlaceholder = document.getElementById('preview-placeholder');
const loader = document.getElementById('loader');

/**
 * Tab switcher function
 */
function switchTab(tabName) {
    if (currentTab === tabName) return;
    
    currentTab = tabName;
    
    // Toggle active buttons
    document.getElementById('aruco-tab-btn').classList.toggle('active', tabName === 'aruco');
    document.getElementById('qr-tab-btn').classList.toggle('active', tabName === 'qr');
    
    // Toggle active contents
    document.getElementById('aruco-content').classList.toggle('active', tabName === 'aruco');
    document.getElementById('qr-content').classList.toggle('active', tabName === 'qr');
    
    // Update main action button text
    const btnGen = document.getElementById('btn-generate');
    if (tabName === 'aruco') {
        btnGen.textContent = 'Generate Marker';
    } else {
        btnGen.textContent = 'Generate QR Code';
    }
    
    // Trigger generation on tab switch
    triggerGeneration();
}

/**
 * Synchronize range slider and number input
 */
function syncSizeInput(type) {
    const slider = document.getElementById(`${type}-size-slider`);
    const numInput = document.getElementById(`${type}-size`);
    numInput.value = slider.value;
    
    // Debounce generation to avoid hammering the server while dragging
    debounceGeneration();
}

function syncSizeSlider(type) {
    const slider = document.getElementById(`${type}-size-slider`);
    const numInput = document.getElementById(`${type}-size`);
    
    // Constrain number input value before syncing
    let val = parseInt(numInput.value) || 400;
    if (val < 50) val = 50;
    if (val > 2000) val = 2000;
    
    slider.value = val;
    debounceGeneration();
}

/**
 * Debounce function to prevent overlapping rapid requests
 */
function debounceGeneration() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        triggerGeneration();
    }, 250);
}

/**
 * Core generation function
 */
function triggerGeneration() {
    // Show loading spinner
    loader.style.display = 'flex';
    
    let url = '';
    
    if (currentTab === 'aruco') {
        const dict = document.getElementById('aruco-dict').value;
        const id = document.getElementById('aruco-id').value || 0;
        const size = document.getElementById('aruco-size').value || 400;
        const padding = document.getElementById('aruco-padding').checked;
        
        url = `/generate/aruco?id=${encodeURIComponent(id)}&dict=${encodeURIComponent(dict)}&size=${encodeURIComponent(size)}&padding=${padding}`;
    } else {
        const data = document.getElementById('qr-data').value || '12345';
        const size = document.getElementById('qr-size').value || 400;
        
        url = `/generate/qr?data=${encodeURIComponent(data)}&size=${encodeURIComponent(size)}`;
    }
    
    // Create new image object to load in background before displaying
    const tempImg = new Image();
    tempImg.onload = function() {
        codePreview.src = url;
        codePreview.style.display = 'block';
        previewPlaceholder.style.display = 'none';
        loader.style.display = 'none';
    };
    
    tempImg.onerror = function() {
        loader.style.display = 'none';
        alert('Failed to generate image. Please check your inputs.');
    };
    
    tempImg.src = url;
}

/**
 * Downloads the current generated image
 */
async function downloadImage() {
    if (!codePreview.src || codePreview.style.display === 'none') {
        alert('No generated code to download yet!');
        return;
    }
    
    try {
        // Fetch the preview image as a blob to allow local saving
        const response = await fetch(codePreview.src);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        
        // Formulate a nice filename
        let filename = 'code.png';
        if (currentTab === 'aruco') {
            const dict = document.getElementById('aruco-dict').value;
            const id = document.getElementById('aruco-id').value || 0;
            filename = `aruco_${dict}_id_${id}.png`;
        } else {
            const rawData = document.getElementById('qr-data').value || 'qr';
            // Sanitize data string for filename
            const cleanData = rawData.replace(/[^a-z0-9]/gi, '_').substring(0, 20);
            filename = `qrcode_${cleanData}.png`;
        }
        
        // Trigger simulated click to download
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error('Error downloading image:', error);
        alert('Could not download image. Please try right-clicking the preview instead.');
    }
}

// Generate the initial preview on page load
document.addEventListener('DOMContentLoaded', () => {
    triggerGeneration();
});
