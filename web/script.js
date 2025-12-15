/**
 * ASCII Face - Global Production Ready
 * Handles Webcam access, ASCII conversion, and Rendering
 */

class AsciiCam {
    constructor() {
        this.video = document.getElementById('webcam-video');
        this.processCanvas = document.getElementById('process-canvas');
        this.ctxProcess = this.processCanvas.getContext('2d', { willReadFrequently: true });
        
        this.asciiCanvas = document.getElementById('ascii-canvas');
        this.ctxAscii = this.asciiCanvas.getContext('2d', { alpha: false });
        
        this.container = document.getElementById('canvas-container');
        
        // Configuration
        this.chars = " .:-=+*#%@"; // Dark to Light
        // Alternative: "Ñ@#W$9876543210?!abc;:+=-,._ "
        this.cols = 120;
        this.fontSize = 0;
        this.running = false;
        this.colorMode = true; // Default to true color
        
        // Bindings
        this.resize = this.resize.bind(this);
        this.loop = this.loop.bind(this);
        
        // UI
        this.permissionOverlay = document.getElementById('permission-message');
        this.startBtn = document.getElementById('start-btn');
        this.toggleColorBtn = document.getElementById('toggle-color-btn');
        this.snapshotBtn = document.getElementById('snapshot-btn');
        
        this.setupEvents();
        window.addEventListener('resize', this.resize);
    }
    
    setupEvents() {
        this.startBtn.addEventListener('click', () => this.start());
        
        this.toggleColorBtn.addEventListener('click', () => {
             this.colorMode = !this.colorMode;
             // Visual feedback could be added here
        });
        
        this.snapshotBtn.addEventListener('click', () => {
            this.takeSnapshot();
        });
    }
    
    async start() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "user"
                }, 
                audio: false 
            });
            
            this.video.srcObject = stream;
            await this.video.play();
            
            this.running = true;
            this.permissionOverlay.classList.add('hidden');
            this.resize();
            requestAnimationFrame(this.loop);
            
        } catch (err) {
            console.error("Camera access denied:", err);
            alert("Could not access camera. Please allow permissions and try again.");
        }
    }
    
    resize() {
        if (!this.running) return;
        
        const aspect = this.video.videoWidth / this.video.videoHeight;
        const containerW = this.container.clientWidth;
        const containerH = this.container.clientHeight;
        
        // Determine layout
        // We want constant COLS.
        // Char aspect ratio is approx 0.6 (width/height).
        // Font Width * Cols = Canvas Width
        // Font Height * Rows = Canvas Height
        
        // Let's maximize canvas in container while keeping aspect ratio
        let canvasW = containerW;
        let canvasH = containerW / aspect;
        
        if (canvasH > containerH) {
            canvasH = containerH;
            canvasW = containerH * aspect;
        }
        
        // High DPI support
        const dpr = window.devicePixelRatio || 1;
        this.asciiCanvas.width = canvasW * dpr;
        this.asciiCanvas.height = canvasH * dpr;
        
        this.asciiCanvas.style.width = `${canvasW}px`;
        this.asciiCanvas.style.height = `${canvasH}px`;
        
        this.ctxAscii.scale(dpr, dpr);
        
        // Processing Canvas Setup
        // We want strict columns.
        this.processCanvas.width = this.cols;
        this.processCanvas.height = Math.floor(this.cols / aspect / 0.5 ); // 0.5 compensates for char height
        
        // Calculate Font Size
        // canvasW / cols
        this.fontSize = canvasW / this.cols;
        this.ctxAscii.font = `${this.fontSize}px 'Fira Code', monospace`;
        this.ctxAscii.textBaseline = 'top';
    }
    
    loop() {
        if (!this.running) return;
        
        const w = this.processCanvas.width;
        const h = this.processCanvas.height;
        
        // 1. Draw small frame
        this.ctxProcess.drawImage(this.video, 0, 0, w, h);
        
        // 2. Get Pixels
        const frameData = this.ctxProcess.getImageData(0, 0, w, h);
        const data = frameData.data; // RGBA
        
        // 3. Clear Screen
        this.ctxAscii.fillStyle = '#050505';
        this.ctxAscii.fillRect(0, 0, this.asciiCanvas.width / (window.devicePixelRatio||1), this.asciiCanvas.height / (window.devicePixelRatio||1));
        
        // 4. Draw Characters
        // Optimization: Batch single-color draws if not true-color?
        // For True Color, we iterate.
        
        const charLen = this.chars.length;
        
        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                const idx = (y * w + x) * 4;
                const r = data[idx];
                const g = data[idx + 1];
                const b = data[idx + 2];
                // const a = data[idx + 3];
                
                // Luminance
                const avg = (r + g + b) / 3;
                
                // Map to Char
                const charIdx = Math.floor((avg / 255) * (charLen - 1));
                const char = this.chars[charIdx];
                
                // Draw
                // X Pos: x * fontSize
                // Y Pos: y * fontSize
                
                if (this.colorMode) {
                    this.ctxAscii.fillStyle = `rgb(${r},${g},${b})`;
                } else {
                    this.ctxAscii.fillStyle = '#00ffbf'; // Matrix Green
                }
                
                this.ctxAscii.fillText(char, x * this.fontSize, y * this.fontSize * 0.6 + (y * this.fontSize * 0.4)); 
                // Line height adjustment is tricky. font is monospace.
                // Usually height approx width / 0.6.
            }
        }
        
        // Add "Scanline" effect or similar if needed?
        // kept simple for performance.
        
        requestAnimationFrame(this.loop);
    }
    
    takeSnapshot() {
        // Create a link to download the canvas image
        const link = document.createElement('a');
        link.download = 'ascii-face-capture.png';
        link.href = this.asciiCanvas.toDataURL('image/png');
        link.click();
        
        // Flash effect
        this.asciiCanvas.style.filter = 'brightness(200%)';
        setTimeout(() => {
            this.asciiCanvas.style.filter = 'none';
        }, 100);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const app = new AsciiCam();
});
