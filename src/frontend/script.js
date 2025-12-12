const pdfUpload = document.getElementById('pdf-upload');
const pdfCanvas = document.getElementById('pdf-render');
const drawCanvas = document.getElementById('draw-layer');
const ctx = pdfCanvas.getContext('2d');
const drawCtx = drawCanvas.getContext('2d');
const container = document.getElementById('pdf-container');
const btnExtract = document.getElementById('btn-extract');
const btnClear = document.getElementById('btn-clear');
const statusLog = document.getElementById('status-log');
const pageInfo = document.getElementById('page-info');
const uploadState = document.getElementById('upload-empty-state');
const pdfContainer = document.getElementById('pdf-container');
const paginationControls = document.getElementById('pagination-controls');
const fileActions = document.getElementById('file-actions');

let pdfDoc = null;
let pageNum = 1;
let pageRendering = false;
let pageNumPending = null;
let scale = 0.6;
let isDrawing = false;
let startX, startY;
let currentRect = null;

function log(msg, type = 'info') {
    const p = document.createElement('p');
    p.textContent = `> ${msg}`;
    p.className = `text-${type}`;
    statusLog.appendChild(p);
    statusLog.scrollTop = statusLog.scrollHeight;
}

function renderPage(num) {
    pageRendering = true;
    pdfDoc.getPage(num).then(function (page) {
        const viewport = page.getViewport({ scale: scale });

        pdfCanvas.height = viewport.height;
        pdfCanvas.width = viewport.width;
        drawCanvas.height = viewport.height;
        drawCanvas.width = viewport.width;

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };
        const renderTask = page.render(renderContext);

        renderTask.promise.then(function () {
            pageRendering = false;
            if (pageNumPending !== null) {
                renderPage(pageNumPending);
                pageNumPending = null;
            }
            document.getElementById('current-page').textContent = num;
            clearDrawings();
        });
    });
}

function queueRenderPage(num) {
    if (pageRendering) {
        pageNumPending = num;
    } else {
        renderPage(num);
    }
}

document.getElementById('prev-page').addEventListener('click', () => {
    if (pageNum <= 1) return;
    pageNum--;
    queueRenderPage(pageNum);
});

document.getElementById('next-page').addEventListener('click', () => {
    if (pageNum >= pdfDoc.numPages) return;
    pageNum++;
    queueRenderPage(pageNum);
});

pdfUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
        log('กรุณาเลือกไฟล์ PDF เท่านั้น', 'error');
        return;
    }

    clearDrawings();
    statusLog.innerHTML = '';

    const fileReader = new FileReader();
    fileReader.onload = function () {
        const typedarray = new Uint8Array(this.result);

        pdfjsLib.getDocument(typedarray).promise.then(function (pdfDoc_) {
            pdfDoc = pdfDoc_;
            document.getElementById('total-pages').textContent = pdfDoc.numPages;
            log(`โหลดไฟล์สำเร็จ: ${file.name} (${pdfDoc.numPages} หน้า)`, 'success');

            uploadState.classList.add('hidden');
            pdfContainer.classList.remove('hidden');
            paginationControls.classList.remove('hidden');
            fileActions.classList.remove('hidden');

            btnExtract.disabled = false;

            pageNum = 1;
            renderPage(pageNum);
        }).catch(err => {
            log('เกิดข้อผิดพลาดในการโหลด PDF: ' + err.message, 'error');
        });
    };
    fileReader.readAsArrayBuffer(file);
});

drawCanvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    const rect = drawCanvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
});

drawCanvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;

    const rect = drawCanvas.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;

    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);

    drawCtx.strokeStyle = '#00ff41';
    drawCtx.lineWidth = 2;
    drawCtx.fillStyle = 'rgba(0, 255, 65, 0.2)';

    const w = currentX - startX;
    const h = currentY - startY;

    drawCtx.fillRect(startX, startY, w, h);
    drawCtx.strokeRect(startX, startY, w, h);
});

drawCanvas.addEventListener('mouseup', (e) => {
    if (!isDrawing) return;
    isDrawing = false;

    const rect = drawCanvas.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    const w = endX - startX;
    const h = endY - startY;

    currentRect = {
        x: Math.min(startX, endX),
        y: Math.min(startY, endY),
        w: Math.abs(w),
        h: Math.abs(h),
        page: pageNum
    };

    if (currentRect.w > 5 && currentRect.h > 5) {
        log(`เลือกพื้นที่แล้ว: [${Math.round(currentRect.x)}, ${Math.round(currentRect.y)}]`, 'success');
    } else {
        currentRect = null;
    }
});

function clearDrawings() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    currentRect = null;
}

btnClear.addEventListener('click', clearDrawings);

btnExtract.addEventListener('click', async () => {

    log('กำลังส่งข้อมูลไปยังเซิร์ฟเวอร์...', 'info');
    btnExtract.disabled = true;

    const fileInput = document.getElementById('pdf-upload');
    if (!fileInput.files[0]) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    if (currentRect) {
        formData.append('x', currentRect.x);
        formData.append('y', currentRect.y);
        formData.append('w', currentRect.w);
        formData.append('h', currentRect.h);
        log('โหมด: แปลงเฉพาะพื้นที่ที่เลือก', 'info');
    } else {
        formData.append('x', 0);
        formData.append('y', 0);
        formData.append('w', pdfCanvas.width);
        formData.append('h', pdfCanvas.height);
        log('โหมด: แปลงข้อมูลทั้งหน้า', 'info');
    }

    formData.append('page', pageNum);
    formData.append('scale', scale);

    try {
        const response = await fetch('http://localhost:5000/extract_region', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            log('แปลงข้อมูลสำเร็จ!', 'success');
            console.log(result);
            alert('ผลลัพธ์: ' + JSON.stringify(result, null, 2));
        } else {
            const err = await response.text();
            log('Error: ' + err, 'error');
        }
    } catch (error) {
        log('Connection Error: ' + error.message, 'error');
    } finally {
        btnExtract.disabled = false;
    }
});