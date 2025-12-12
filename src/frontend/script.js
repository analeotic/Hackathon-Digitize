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

// Store last result for preview
let lastExtractedResult = null;

btnExtract.addEventListener('click', async () => {

    log('กำลังส่งข้อมูลไปยังเซิร์ฟเวอร์...', 'info');
    btnExtract.disabled = true;

    const fileInput = document.getElementById('pdf-upload');
    if (!fileInput.files[0]) return;

    // Show loading overlay
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingStep = document.getElementById('loading-step');
    loadingOverlay.classList.remove('hidden');

    // Loading step animation
    const loadingSteps = [
        '📄 กำลังอ่านเอกสาร...',
        '🔍 วิเคราะห์โครงสร้างเอกสาร...',
        '🤖 AI กำลังประมวลผล...',
        '📊 แปลงข้อมูลเป็น CSV...',
        '✨ กำลังสรุปผลลัพธ์...'
    ];
    let stepIndex = 0;
    const stepInterval = setInterval(() => {
        stepIndex = (stepIndex + 1) % loadingSteps.length;
        loadingStep.textContent = loadingSteps[stepIndex];
    }, 2000);

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
        const response = await fetch('/extract_region', {
            method: 'POST',
            body: formData
        });

        // Hide loading overlay
        clearInterval(stepInterval);
        loadingOverlay.classList.add('hidden');

        if (response.ok) {
            const result = await response.json();
            lastExtractedResult = result;
            log('✅ แปลงข้อมูลสำเร็จ!', 'success');

            // Display confidence scores in sidebar
            const confidenceDisplay = document.getElementById('confidence-display');
            if (result.confidence) {
                const conf = result.confidence;
                const overall = (conf.overall * 100).toFixed(1);
                const stats = conf.field_stats;

                confidenceDisplay.innerHTML = `
                    <div class="confidence-label">ความแม่นยำโดยรวม</div>
                    <div class="confidence-score">${overall}%</div>
                    <div class="confidence-stats">
                        <span class="stat-high">✅ ${stats.high_confidence || 0}</span>
                        <span class="stat-medium">⚠️ ${stats.medium_confidence || 0}</span>
                        <span class="stat-low">❌ ${stats.low_confidence || 0}</span>
                    </div>
                `;

                // Log detailed confidence info
                log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'info');
                log(`📊 CONFIDENCE SCORE REPORT`, 'info');
                log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'info');
                log(`Overall Confidence: ${overall}%`, 'success');
                log(``, 'info');
                log(`Field Statistics:`, 'info');
                log(`  Total Fields: ${stats.total || 0}`, 'info');
                log(`  ✅ High (≥90%):   ${stats.high_confidence || 0}`, 'success');
                log(`  ⚠️  Medium (70-90%): ${stats.medium_confidence || 0}`, 'info');
                log(`  ❌ Low (<70%):    ${stats.low_confidence || 0}`, stats.low_confidence > 0 ? 'error' : 'info');

                if (conf.low_confidence_fields && conf.low_confidence_fields.length > 0) {
                    log(``, 'info');
                    log(`⚠️  Low Confidence Fields:`, 'error');
                    conf.low_confidence_fields.slice(0, 5).forEach(field => {
                        const confPct = (field.confidence * 100).toFixed(0);
                        log(`  - ${field.field}: ${confPct}%`, 'error');
                    });
                }

                if (conf.warnings && conf.warnings.length > 0) {
                    log(``, 'info');
                    log(`❗ Validation Warnings:`, 'error');
                    conf.warnings.slice(0, 5).forEach(warning => {
                        log(`  - ${warning}`, 'error');
                    });
                }

                log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'info');
            }

            // Display CSV files
            if (result.output && result.output.csv_files) {
                log(`📁 Generated ${result.output.count} CSV files`, 'success');

                const resultsSidebar = document.getElementById('results-sidebar');
                const downloadList = document.getElementById('download-list');
                const previewBtn = document.getElementById('btn-preview-data');

                // Clear previous results and show right sidebar
                downloadList.innerHTML = '';
                resultsSidebar.classList.remove('hidden');

                result.output.csv_files.forEach(filename => {
                    const btn = document.createElement('a');
                    btn.href = `/download/${filename}`;
                    btn.textContent = `📄 ${filename}`;
                    btn.download = filename;
                    btn.onclick = (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        fetch(btn.href)
                            .then(res => res.blob())
                            .then(blob => {
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = filename;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                URL.revokeObjectURL(url);
                                log(`✅ ดาวน์โหลด ${filename} สำเร็จ`, 'success');
                            })
                            .catch(err => log('Download error: ' + err.message, 'error'));
                        return false;
                    };

                    downloadList.appendChild(btn);
                });

                // Show preview button
                previewBtn.style.display = 'block';
                previewBtn.onclick = () => showDataPreviewModal(result.data);

                log('✅ ดูผลลัพธ์ได้ที่แถบด้านขวา', 'success');
            }

            console.log('Full result:', result);
        } else {
            const err = await response.text();
            log('❌ Error: ' + err, 'error');
        }
    } catch (error) {
        // Hide loading overlay on error
        clearInterval(stepInterval);
        loadingOverlay.classList.add('hidden');

        log('Connection Error: ' + error.message, 'error');
        log('ℹ️ ตรวจสอบว่า API Server กำลังทำงานอยู่ที่ port 5001', 'info');
    } finally {
        btnExtract.disabled = false;
    }
});

// Data Preview Modal
function showDataPreviewModal(data) {
    if (!data) return;

    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => {
        if (e.target === overlay) overlay.remove();
    };

    // Create modal content
    const modal = document.createElement('div');
    modal.className = 'modal-content';

    // Header
    const header = document.createElement('div');
    header.className = 'modal-header';
    header.innerHTML = `
        <h2>📊 ข้อมูลที่แปลงได้</h2>
        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
    `;
    modal.appendChild(header);

    // Body
    const body = document.createElement('div');
    body.className = 'modal-body';

    // Create tables for each data type
    let content = '';

    // Assets
    if (data.assets && data.assets.length > 0) {
        content += `<h3>📦 ทรัพย์สิน (Assets): ${data.assets.length} รายการ</h3>`;
        content += `<table class="data-table">
            <thead>
                <tr><th>#</th><th>ประเภท</th><th>ชื่อ</th><th>มูลค่า</th><th>เจ้าของ</th></tr>
            </thead>
            <tbody>`;
        data.assets.forEach((asset, i) => {
            const owner = [];
            if (asset.owner_by_submitter) owner.push('ผู้ยื่น');
            if (asset.owner_by_spouse) owner.push('คู่สมรส');
            if (asset.owner_by_child) owner.push('บุตร');
            content += `<tr>
                <td>${i + 1}</td>
                <td>${asset.asset_type_id || '-'}</td>
                <td>${asset.asset_name || '-'}</td>
                <td>${asset.valuation?.toLocaleString() || '-'}</td>
                <td>${owner.join(', ') || '-'}</td>
            </tr>`;
        });
        content += `</tbody></table><br>`;
    }

    // Statements
    if (data.statements && data.statements.length > 0) {
        content += `<h3>📝 รายการ (Statements): ${data.statements.length} รายการ</h3>`;
        content += `<table class="data-table">
            <thead>
                <tr><th>#</th><th>ประเภท</th><th>มูลค่า</th><th>เจ้าของ</th></tr>
            </thead>
            <tbody>`;
        data.statements.forEach((stmt, i) => {
            const owner = [];
            if (stmt.owner_by_submitter) owner.push('ผู้ยื่น');
            if (stmt.owner_by_spouse) owner.push('คู่สมรส');
            if (stmt.owner_by_child) owner.push('บุตร');
            content += `<tr>
                <td>${i + 1}</td>
                <td>${stmt.statement_type_id || '-'}</td>
                <td>${stmt.valuation?.toLocaleString() || '-'}</td>
                <td>${owner.join(', ') || '-'}</td>
            </tr>`;
        });
        content += `</tbody></table><br>`;
    }

    // Positions
    if (data.submitter_positions && data.submitter_positions.length > 0) {
        content += `<h3>👔 ตำแหน่ง (Positions): ${data.submitter_positions.length} รายการ</h3>`;
        content += `<table class="data-table">
            <thead>
                <tr><th>#</th><th>ตำแหน่ง</th><th>หน่วยงาน</th><th>ปีที่เริ่ม</th></tr>
            </thead>
            <tbody>`;
        data.submitter_positions.forEach((pos, i) => {
            content += `<tr>
                <td>${i + 1}</td>
                <td>${pos.position_title || '-'}</td>
                <td>${pos.position_agency || '-'}</td>
                <td>${pos.position_start_year || '-'}</td>
            </tr>`;
        });
        content += `</tbody></table><br>`;
    }

    // Relatives
    if (data.relatives && data.relatives.length > 0) {
        content += `<h3>👨‍👩‍👧‍👦 ญาติ (Relatives): ${data.relatives.length} คน</h3>`;
        content += `<table class="data-table">
            <thead>
                <tr><th>#</th><th>ชื่อ</th><th>นามสกุล</th><th>ความสัมพันธ์</th><th>อายุ</th></tr>
            </thead>
            <tbody>`;
        data.relatives.forEach((rel, i) => {
            content += `<tr>
                <td>${i + 1}</td>
                <td>${rel.first_name || '-'}</td>
                <td>${rel.last_name || '-'}</td>
                <td>${rel.relationship_id || '-'}</td>
                <td>${rel.age || '-'}</td>
            </tr>`;
        });
        content += `</tbody></table><br>`;
    }

    // Spouse
    if (data.spouse_info) {
        content += `<h3>💑 คู่สมรส (Spouse)</h3>`;
        content += `<table class="data-table">
            <tbody>
                <tr><th>ชื่อ</th><td>${data.spouse_info.first_name || '-'}</td></tr>
                <tr><th>นามสกุล</th><td>${data.spouse_info.last_name || '-'}</td></tr>
                <tr><th>อาชีพ</th><td>${data.spouse_info.occupation || '-'}</td></tr>
                <tr><th>อายุ</th><td>${data.spouse_info.age || '-'}</td></tr>
            </tbody>
        </table><br>`;
    }

    if (!content) {
        content = '<p style="text-align:center; color:#888;">ไม่พบข้อมูลที่แปลงได้</p>';
    }

    body.innerHTML = content;
    modal.appendChild(body);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}