// scanner.js - QR/Barcode scanning logic with html5-qrcode library

let scanner;
let isScanning = false;

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-scan-btn');
    const stopBtn = document.getElementById('stop-scan-btn');
    const resultDiv = document.getElementById('scan-result');
    
    // Check authentication
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    // Event listeners
    if (startBtn) {
        startBtn.addEventListener('click', startScanning);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopScanning);
    }
    
    function startScanning() {
        if (isScanning) return;
        
        isScanning = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        resultDiv.innerHTML = '';
        
        try {
            scanner = new Html5Qrcode("scanner-container");
            
            const config = {
                fps: 10,
                qrbox: 250,
                aspectRatio: 1.0
            };
            
            scanner.start(
                { facingMode: "environment" },
                config,
                onScanSuccess
            ).catch(err => {
                console.error('Failed to start scanner:', err);
                showResult('Error: Could not access camera. Please check permissions.', 'error');
                resetScanner();
            });
            
        } catch (err) {
            console.error('Scanner error:', err);
            showResult('Error initializing scanner', 'error');
            resetScanner();
        }
    }
    
    window.startScanning = startScanning;
    window.stopScanning = stopScanning;
    
    function stopScanning() {
        if (!isScanning || !scanner) return;
        
        isScanning = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        
        try {
            scanner.stop().then(() => {
                if (scanner) {
                    scanner.clear();
                    scanner = null;
                }
                showResult('Scanner stopped', 'info');
            }).catch(err => {
                console.error('Error stopping scanner:', err);
                if (scanner) {
                    scanner = null;
                }
            });
        } catch (err) {
            console.error('Error in stopScanning:', err);
            scanner = null;
        }
    }
    
    function onScanSuccess(decodedText, decodedResult) {
        // Process the scanned barcode
        console.log('Scanned barcode:', decodedText);
        
        showResult(`Barcode Scanned: ${decodedText}`, 'success');
        
        // Send to backend
        processScan(decodedText);
    }
    
    function processScan(barcode) {
        const token = localStorage.getItem('authToken');
        const orderId = new URLSearchParams(window.location.search).get('order_id');
        
        if (!orderId) {
            showResult('Please select an order first', 'error');
            return;
        }
        
        fetch('/api/scan/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                barcode: barcode,
                order_id: orderId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'mismatch') {
                showResult(`Mismatch: ${data.message}`, 'mismatch');
            } else {
                showResult(`Verified: ${data.message}`, 'success');
            }
        })
        .catch(err => {
            console.error('Error processing scan:', err);
            showResult('Error processing scan', 'error');
        });
    }
    
    function showResult(message, type = 'success') {
        const result = document.createElement('div');
        result.className = `scan-result result-${type}`;
        result.innerText = message;
        resultDiv.innerHTML = '';
        resultDiv.appendChild(result);
        
        // Auto-hide success messages after 3 seconds
        if (type === 'success') {
            setTimeout(() => {
                if (result.parentNode) {
                    result.remove();
                }
            }, 3000);
        }
    }
    
    function resetScanner() {
        isScanning = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        if (scanner) {
            scanner = null;
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
});