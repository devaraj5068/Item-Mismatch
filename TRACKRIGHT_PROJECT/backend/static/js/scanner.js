// scanner.js - Barcode scanner functionality

let html5QrCode = null;
let currentOrderId = null;
let isScanning = false;

document.addEventListener('DOMContentLoaded', function() {
    // Setup UI
    setupScannerButtons();
    setupBarcodeInput();
    loadScanHistory();
    setupLogout();
    
    // Load html5-qrcode library
    loadHtml5Qrcode().then(() => {
        console.log('Html5Qrcode library loaded');
    }).catch(err => {
        console.error('Failed to load Html5Qrcode:', err);
        showToast('Failed to load scanner library', 'error');
    });
});

function setupScannerButtons() {
    const startBtn = document.getElementById('start-scan-btn');
    const stopBtn = document.getElementById('stop-scan-btn');
    
    if (startBtn) {
        startBtn.addEventListener('click', function(e) {
            e.preventDefault();
            startScanning();
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            stopScanning();
        });
    }
}

async function initializeScanner() {
    // Load html5-qrcode library
    if (!window.Html5Qrcode) {
        await loadHtml5Qrcode();
    }

    const scannerElement = document.getElementById('scanner');

    if (scannerElement && window.Html5Qrcode) {
        if (!html5QrCode) {
            html5QrCode = new Html5Qrcode("scanner");
        }

        // Get order ID from URL (optional - can scan without specifying order)
        currentOrderId = getOrderIdFromUrl();
    }
}

function getOrderIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('order_id');
}

async function startScanning() {
    if (isScanning || !html5QrCode) {
        initializeScanner().then(() => {
            continueStartScanning();
        });
        return;
    }
    continueStartScanning();
}

async function continueStartScanning() {
    if (!window.Html5Qrcode) {
        await loadHtml5Qrcode();
    }

    if (!html5QrCode) {
        html5QrCode = new Html5Qrcode("scanner");
    }

    const scannerElement = document.getElementById('scanner');
    if (!scannerElement) {
        showToast('Scanner element not found', 'error');
        return;
    }

    isScanning = true;
    const startBtn = document.getElementById('start-scan-btn');
    const stopBtn = document.getElementById('stop-scan-btn');
    
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.style.opacity = '0.5';
        startBtn.style.cursor = 'not-allowed';
    }
    if (stopBtn) {
        stopBtn.disabled = false;
        stopBtn.style.opacity = '1';
        stopBtn.style.cursor = 'pointer';
        stopBtn.style.display = 'inline-block';
    }

    try {
        await html5QrCode.start(
            { facingMode: "environment" }, // Use back camera
            {
                fps: 10,
                qrbox: { width: 250, height: 250 }
            },
            onScanSuccess,
            onScanFailure
        );

        showToast('✅ Scanner started! Point camera at barcode.', 'success');
    } catch (error) {
        console.error('Error starting scanner:', error);
        isScanning = false;
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.style.opacity = '1';
            startBtn.style.cursor = 'pointer';
        }
        if (stopBtn) {
            stopBtn.disabled = true;
            stopBtn.style.opacity = '0.5';
            stopBtn.style.cursor = 'not-allowed';
            stopBtn.style.display = 'none';
        }
        
        if (error.name === 'NotAllowedError') {
            showToast('❌ Camera access denied. Please enable camera permissions.', 'error');
        } else if (error.name === 'NotFoundError') {
            showToast('❌ No camera found on this device.', 'error');
        } else {
            showToast('❌ Error starting camera: ' + error.message, 'error');
        }
    }
}

async function stopScanning() {
    if (!isScanning || !html5QrCode) return;

    isScanning = false;
    const startBtn = document.getElementById('start-scan-btn');
    const stopBtn = document.getElementById('stop-scan-btn');
    
    try {
        await html5QrCode.stop();
        showToast('⏹️ Scanner stopped', 'success');
    } catch (error) {
        console.error('Error stopping scanner:', error);
    }

    if (startBtn) {
        startBtn.disabled = false;
        startBtn.style.opacity = '1';
        startBtn.style.cursor = 'pointer';
    }
    if (stopBtn) {
        stopBtn.disabled = true;
        stopBtn.style.opacity = '0.5';
        stopBtn.style.cursor = 'not-allowed';
        stopBtn.style.display = 'none';
    }
}

function onScanSuccess(decodedText, decodedResult) {
    // Stop scanning temporarily
    html5QrCode.pause();

    // Always use the unified barcode verification endpoint
    verifyBarcode(decodedText);

    // Resume scanning after a delay
    setTimeout(() => {
        html5QrCode.resume();
    }, 2000);
}

async function verifyBarcode(barcode) {
    try {
        const response = await fetch('/scan/verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `barcode=${encodeURIComponent(barcode)}`
        });
        if (response.status === 401) {
            showToast('❌ Login required to verify barcodes', 'error');
            return;
        }
        const data = await response.json();

        // Populate the product/status fields directly
        const expectedEl = document.getElementById('expected-product');
        const scannedEl = document.getElementById('scanned-product');
        const statusEl = document.getElementById('scan-status');

        if (expectedEl) expectedEl.innerText = data.expected_product || 'N/A';
        if (scannedEl) scannedEl.innerText = data.scanned_product || 'N/A';

        if (statusEl) {
            if (data.status === 'verified') {
                statusEl.innerHTML = '<span style="color:green;font-weight:bold">✅ Verified</span>';
            } else {
                statusEl.innerHTML = '<span style="color:red;font-weight:bold">❌ Mismatch</span>';
            }
        }

        if (data.success) {
            showToast(`✅ Verified: ${data.expected_product}`, 'success');
        } else {
            showToast(`❌ ${data.message || 'Invalid barcode'}`, 'error');
        }

        // Reload page to update counters
        setTimeout(() => {
            location.reload();
        }, 1500);
        
    } catch (err) {
        console.error('Barcode verify error', err);
        showToast('Error verifying barcode', 'error');
    }
}

function onScanFailure(error) {
    // Ignore scan failures - they're normal
}

async function processBarcode(barcode) {
    // Allow scanning without specific order - just record the scan
    try {
        const token = localStorage.getItem('auth_token');
        const url = '/api/scan/';
        const body = {
            barcode: barcode,
        };
        
        // Add order_id if available
        if (currentOrderId) {
            body.order_id = currentOrderId;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(body)
        });

        const result = await response.json();

        if (response.ok) {
            // Update scan results UI
            updateScanResults(result);
            
            if (result.status === 'verified' || result.status === 'success') {
                showToast(`✅ Verified: ${result.message || barcode}`, 'success');
                updateScanStats();
                loadScanHistory();
            } else if (result.status === 'mismatch') {
                showToast(`⚠️ Mismatch: ${result.message}`, 'warning');
                loadScanHistory();
            } else {
                showToast(`ℹ️ ${result.message || 'Scanned: ' + barcode}`, 'info');
                loadScanHistory();
            }
        } else {
            showToast(`❌ Error: ${result.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error processing barcode:', error);
        showToast('❌ Error processing barcode: ' + error.message, 'error');
    }
}

function updateScanResults(result) {
    const expectedProductEl = document.getElementById('expected-product');
    const scannedProductEl = document.getElementById('scanned-product');
    const scanStatusEl = document.getElementById('scan-status');
    
    // determine success flag: prefer explicit, fall back to "verified" status
    const successFlag = (typeof result.success === 'boolean')
        ? result.success
        : (result.status === 'verified');

    if (expectedProductEl) {
        expectedProductEl.textContent = result.expected_product || 'N/A';
        expectedProductEl.style.color = successFlag ? '#10b981' : '#ef4444';
    }
    
    if (scannedProductEl) {
        scannedProductEl.textContent = result.scanned_product || 'N/A';
        scannedProductEl.style.color = successFlag ? '#10b981' : '#ef4444';
    }
    
    if (scanStatusEl) {
        const statusText = result.status ? result.status.charAt(0).toUpperCase() + result.status.slice(1) : 'Unknown';
        scanStatusEl.textContent = successFlag ? `✅ ${statusText}` : `❌ ${statusText}`;
        scanStatusEl.style.color = successFlag ? '#10b981' : '#ef4444';
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setupBarcodeInput() {
    const barcodeInput = document.getElementById('barcode-input');
    if (barcodeInput) {
        barcodeInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const barcode = e.target.value.trim();
                if (barcode) {
                    processBarcode(barcode);
                    e.target.value = '';
                }
            }
        });
    }
}

async function loadScanHistory() {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('/api/scans/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const scans = await response.json();
            const scansList = Array.isArray(scans) ? scans : scans.results || [];

            const tbody = document.getElementById('scan-history');
            if (tbody && scansList.length > 0) {
                tbody.innerHTML = scansList.slice(0, 10).map(scan => {
                    const statusHtml = scan.status === 'verified'
                        ? '<span class="badge badge-success">✅ Verified</span>'
                        : '<span class="badge badge-danger">❌ Mismatch</span>';
                    return `
                    <tr>
                        <td>${scan.barcode}</td>
                        <td>${scan.product_name || scan.order_number || 'Unknown'}</td>
                        <td>${statusHtml}</td>
                        <td>${new Date(scan.scanned_at).toLocaleTimeString()}</td>
                    </tr>
                `}).join('');
            }
        }
    } catch (error) {
        console.error('Error loading scan history:', error);
    }
}

async function updateScanStats() {
    try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('/api/dashboard/stats/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const stats = await response.json();
            document.getElementById('scans-today').textContent = stats.todays_scans || 0;
            // Note: We don't have separate matches/mismatches in current stats
            // Could be enhanced to show these separately
        }
    } catch (error) {
        console.error('Error updating scan stats:', error);
    }
}

function getStatusBadgeColor(status) {
    switch (status) {
        case 'verified': return 'success';
        case 'mismatch': return 'danger';
        case 'unknown': return 'warning';
        default: return 'primary';
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function loadHtml5Qrcode() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

function setupLogout() {
    const logoutBtn = document.getElementById('logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (html5QrCode) {
                html5QrCode.stop().then(() => {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/accounts/login/';
                });
            } else {
                localStorage.removeItem('auth_token');
                window.location.href = '/accounts/login/';
            }
        });
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (html5QrCode) {
        html5QrCode.stop();
    }
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}

@keyframes slideOut {
    from { transform: translateX(0); }
    to { transform: translateX(100%); }
}
`;
document.head.appendChild(style);