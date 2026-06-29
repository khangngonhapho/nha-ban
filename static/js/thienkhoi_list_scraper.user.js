// ==UserScript==
// @name         Khang Ngô BDS - Thiên Khôi List Scraper
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Cào nhanh thông tin nhà phố từ danh sách Thiên Khôi về local server Khang Ngô
// @author       Antigravity
// @match        https://*.thienkhoi.com/*
// @match        http://*.thienkhoi.com/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @connect      127.0.0.1
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // CONFIGURATION
    let localPort = '5000';
    try {
        localPort = localStorage.getItem('kn_scraper_port') || '5000';
    } catch (e) {
        console.warn("[Khang Ngô BDS] Không thể truy cập localStorage:", e);
    }
    let getLocalUrl = () => `http://localhost:${localPort}`;

    // STYLES
    const styles = `
        /* Injected Card Button */
        .kn-scrape-btn {
            width: 100%;
            margin-top: 8px;
            background-color: #E31A22;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s ease-in-out;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            box-shadow: 0 2px 4px rgba(227, 26, 34, 0.2);
        }
        .kn-scrape-btn:hover {
            background-color: #b7141a;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(227, 26, 34, 0.3);
        }
        .kn-scrape-btn:active {
            transform: translateY(0);
        }
        .kn-scrape-btn.crawling {
            background-color: #6b7280 !important;
            cursor: not-allowed;
            box-shadow: none;
        }
        .kn-scrape-btn.success {
            background-color: #10b981 !important;
            box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
        }
        .kn-scrape-btn.failed {
            background-color: #374151 !important;
            box-shadow: none;
        }

        /* Spinner Animation */
        .kn-spinner {
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: kn-spin 0.8s linear infinite;
        }
        @keyframes kn-spin {
            to { transform: rotate(360deg); }
        }

        /* Floating Control Panel */
        #kn-floating-panel {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            max-height: 450px;
            background: rgba(18, 18, 18, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
            color: #ffffff;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            z-index: 99999;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        #kn-floating-panel.collapsed {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            overflow: hidden;
        }
        
        /* Panel Header */
        .kn-panel-header {
            padding: 14px 16px;
            background: rgba(227, 26, 34, 0.15);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        .kn-panel-title {
            font-weight: 700;
            font-size: 14px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .kn-panel-title span.logo-dot {
            width: 8px;
            height: 8px;
            background-color: #E31A22;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #E31A22;
        }
        .kn-panel-toggle {
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            font-size: 16px;
            cursor: pointer;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: color 0.2s;
        }
        .kn-panel-toggle:hover {
            color: #ffffff;
        }

        /* Panel Body */
        .kn-panel-body {
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
            flex: 1;
        }
        #kn-floating-panel.collapsed .kn-panel-body {
            display: none;
        }
        
        .kn-stat-row {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }
        .kn-stat-val {
            font-weight: 700;
            color: #ffffff;
        }

        /* Listings Checklist */
        .kn-listings-list {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.2);
            max-height: 150px;
            overflow-y: auto;
            padding: 6px;
        }
        .kn-list-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px;
            font-size: 11px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .kn-list-item:last-child {
            border-bottom: none;
        }
        .kn-list-item input[type="checkbox"] {
            accent-color: #E31A22;
            cursor: pointer;
        }
        .kn-item-title {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            color: rgba(255, 255, 255, 0.85);
        }
        
        /* Actions Area */
        .kn-actions-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .kn-btn-primary {
            grid-column: span 2;
            background: #E31A22;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 4px 12px rgba(227, 26, 34, 0.3);
        }
        .kn-btn-primary:hover {
            background: #b7141a;
        }
        .kn-btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px;
            font-size: 11px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }
        .kn-btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        /* Config Panel */
        .kn-config-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 10px;
        }
        .kn-config-label {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.6);
        }
        .kn-config-input {
            width: 60px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            color: white;
            padding: 2px 6px;
            font-size: 11px;
            text-align: center;
        }

        /* Mini Logs */
        .kn-logs-box {
            font-family: monospace;
            font-size: 10px;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            padding: 6px;
            height: 60px;
            overflow-y: auto;
            color: #84cc16;
            white-space: pre-wrap;
        }

        /* Notification Toast */
        .kn-toast {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 24px;
            background: rgba(31, 41, 55, 0.9);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            z-index: 100000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            pointer-events: none;
            transition: all 0.3s ease;
            opacity: 0;
        }
        .kn-toast.show {
            opacity: 1;
            top: 30px;
        }
        
        /* Floating Icon mode when collapsed */
        .kn-collapsed-icon {
            display: none;
            width: 100%;
            height: 100%;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            background: #E31A22;
            transition: background 0.2s;
        }
        .kn-collapsed-icon:hover {
            background: #b7141a;
        }
        #kn-floating-panel.collapsed .kn-collapsed-icon {
            display: flex;
        }
    `;

    // Deferred DOM initialization to prevent errors if document.body/head is not ready
    let domInitialized = false;
    let toastEl = null;

    function initializeDOM() {
        if (domInitialized) return;
        if (!document.head || !document.body) return;

        try {
            // Inject CSS
            const styleEl = document.createElement('style');
            styleEl.textContent = styles;
            document.head.appendChild(styleEl);

            // Toast element
            toastEl = document.createElement('div');
            toastEl.className = 'kn-toast';
            document.body.appendChild(toastEl);

            domInitialized = true;
            console.log("[Khang Ngô BDS Scraper] Khởi tạo DOM (style/toast) thành công.");
        } catch (e) {
            console.error("[Khang Ngô BDS Scraper] Lỗi khởi tạo DOM:", e);
        }
    }

    function showToast(message, duration = 3000) {
        if (!toastEl) return;
        toastEl.textContent = message;
        toastEl.classList.add('show');
        setTimeout(() => {
            if (toastEl) toastEl.classList.remove('show');
        }, duration);
    }

    // STATE STORE
    let detectedListings = [];
    let isCrawlingBulk = false;
    let localListingIds = new Set();
    let checkedIds = new Set(); // Cache verified listing IDs to prevent duplicate calls
    let uncheckedPanelIds = new Set(); // Track manually unchecked IDs in the panel
    let runAi = false;
    try {
        runAi = localStorage.getItem('kn_run_ai') === 'true';
    } catch (e) {}

    // CHECK A BATCH OF LISTING IDS FOR LOCAL EXISTENCE
    function checkExistLocally(tkIds) {
        const idsToCheck = tkIds.map(id => id.toLowerCase()).filter(id => !checkedIds.has(id));
        if (idsToCheck.length === 0) return Promise.resolve(true);

        return new Promise((resolve) => {
            GM_xmlhttpRequest({
                method: "POST",
                url: `${getLocalUrl()}/api/listings/check-exist`,
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify({ tk_ids: idsToCheck }),
                onload: function(response) {
                    if (response.status === 200) {
                        try {
                            const resData = JSON.parse(response.responseText);
                            const exists = resData.exists || [];
                            exists.forEach(id => {
                                localListingIds.add(id.toLowerCase());
                            });
                            // Mark all these IDs as verified
                            idsToCheck.forEach(id => checkedIds.add(id));
                            console.log(`[Khang Ngô BDS Scraper] Đã kiểm tra ${idsToCheck.length} căn mới. Phát hiện ${exists.length} căn đã cào.`);
                            resolve(true);
                        } catch (e) {
                            console.error("[Khang Ngô BDS Scraper] Lỗi parse phản hồi check-exist:", e);
                            resolve(false);
                        }
                    } else {
                        resolve(false);
                    }
                },
                onerror: function(err) {
                    console.warn("[Khang Ngô BDS Scraper] Không thể kết nối local server để kiểm tra tồn tại căn.");
                    resolve(false);
                }
            });
        });
    }

    // HELPER: Add message to log panel
    function writeLog(msg) {
        const logBox = document.getElementById('kn-logs');
        if (logBox) {
            const timeStr = new Date().toLocaleTimeString();
            logBox.textContent += `[${timeStr}] ${msg}\n`;
            logBox.scrollTop = logBox.scrollHeight;
        }
    }

    // AUTO-SYNC COOKIES ON LAUNCH
    function syncCookies() {
        return new Promise((resolve) => {
            writeLog("Đang đồng bộ cookie với server...");
            GM_xmlhttpRequest({
                method: "POST",
                url: `${getLocalUrl()}/api/crawl`,
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify({
                    url: "MOCK_SAVE_ONLY",
                    cookie: document.cookie
                }),
                onload: function(response) {
                    if (response.status === 200) {
                        writeLog("✅ Đồng bộ cookie thành công!");
                        resolve(true);
                    } else {
                        writeLog(`❌ Lỗi đồng bộ cookie: HTTP ${response.status}`);
                        resolve(false);
                    }
                },
                onerror: function(err) {
                    writeLog("❌ Không kết nối được server local. Hãy bật manager.py!");
                    resolve(false);
                }
            });
        });
    }

    // TRIGGER SINGLE LISTING CRAWL
    async function crawlSingle(tkId, buttonEl, title = '') {
        if (!buttonEl) return;
        
        buttonEl.disabled = true;
        buttonEl.className = "kn-scrape-btn crawling";
        buttonEl.innerHTML = `<div class="kn-spinner"></div> Đang cào...`;
        
        writeLog("Đang làm mới cookie trước khi cào...");
        await syncCookies();
        
        writeLog(`Bắt đầu cào căn: ${tkId.slice(0, 8)}...`);

        GM_xmlhttpRequest({
            method: "POST",
            url: `${getLocalUrl()}/api/listings/${tkId}/recrawl`,
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify({ run_ai: runAi, title: title }),
            timeout: 60000,
            onload: function(response) {
                buttonEl.disabled = false;
                try {
                    const resData = JSON.parse(response.responseText);
                    if (response.status === 200 && resData.status === "success") {
                        buttonEl.className = "kn-scrape-btn success";
                        buttonEl.innerHTML = `✅ Đã có`;
                        buttonEl.title = "Căn này đã có trong database local. Nhấn để cào lại.";
                        writeLog(`✅ Cào thành công căn: ${tkId.slice(0, 8)}`);
                        showToast(`Cào thành công căn!`);
                        localListingIds.add(tkId.toLowerCase());
                        updateFloatingPanel();
                    } else {
                        const errMsg = resData.message || "Lỗi chưa rõ";
                        buttonEl.className = "kn-scrape-btn failed";
                        buttonEl.innerHTML = `❌ Thất bại`;
                        buttonEl.title = errMsg;
                        writeLog(`❌ Thất bại: ${errMsg}`);
                        showToast(`Lỗi: ${errMsg}`);
                    }
                } catch(e) {
                    buttonEl.className = "kn-scrape-btn failed";
                    buttonEl.innerHTML = `❌ Lỗi phản hồi`;
                    writeLog(`❌ Lỗi parse JSON phản hồi.`);
                }
            },
            onerror: function(err) {
                buttonEl.disabled = false;
                buttonEl.className = "kn-scrape-btn failed";
                buttonEl.innerHTML = `❌ Mất kết nối`;
                writeLog(`❌ Không thể gửi request tới local server.`);
                showToast("Lỗi kết nối server local!");
            }
        });
    }

    // BULK CRAWL
    async function crawlBulk() {
        if (isCrawlingBulk) return;
        
        const checkboxes = document.querySelectorAll('.kn-item-check:checked');
        if (checkboxes.length === 0) {
            showToast("Vui lòng chọn ít nhất 1 căn để cào!");
            return;
        }

        isCrawlingBulk = true;
        
        writeLog("Đang làm mới cookie trước khi cào hàng loạt...");
        await syncCookies();
        
        writeLog(`🚀 BẮT ĐẦU CÀO HÀNG LOẠT ${checkboxes.length} CĂN...`);
        const bulkBtn = document.getElementById('kn-btn-bulk-scrape');
        if (bulkBtn) bulkBtn.textContent = "Đang cào hàng loạt...";

        let isAuthError = false;
        for (let i = 0; i < checkboxes.length; i++) {
            if (isAuthError) {
                writeLog("🚨 Đã dừng cào hàng loạt do lỗi xác thực.");
                break;
            }
            const tkId = checkboxes[i].value;
            const item = detectedListings.find(l => l.id === tkId);
            const title = item ? item.title : '';
            writeLog(`[${i+1}/${checkboxes.length}] Đang xử lý: ${tkId}`);
            
            // Find corresponding card button to update its UI state
            const cardBtn = document.querySelector(`.kn-scrape-btn[data-tk-id="${tkId}"]`);
            
            await new Promise((resolve) => {
                if (cardBtn) {
                    cardBtn.disabled = true;
                    cardBtn.className = "kn-scrape-btn crawling";
                    cardBtn.innerHTML = `<div class="kn-spinner"></div> Đang cào...`;
                }

                GM_xmlhttpRequest({
                    method: "POST",
                    url: `${getLocalUrl()}/api/listings/${tkId}/recrawl`,
                    headers: {
                        "Content-Type": "application/json"
                    },
                    data: JSON.stringify({ run_ai: runAi, title: title }),
                    timeout: 60000,
                    onload: function(response) {
                        try {
                            const resData = JSON.parse(response.responseText);
                            if (response.status === 200 && resData.status === "success") {
                                if (cardBtn) {
                                    cardBtn.className = "kn-scrape-btn success";
                                    cardBtn.innerHTML = `✅ Đã có`;
                                    cardBtn.title = "Căn này đã có trong database local. Nhấn để cào lại.";
                                }
                                writeLog(`✅ [${i+1}/${checkboxes.length}] Thành công: ${tkId.slice(0, 8)}`);
                                localListingIds.add(tkId.toLowerCase());
                            } else {
                                if (cardBtn) {
                                    cardBtn.className = "kn-scrape-btn failed";
                                    cardBtn.innerHTML = `❌ Thất bại`;
                                    cardBtn.title = resData.message;
                                }
                                writeLog(`❌ [${i+1}/${checkboxes.length}] Thất bại: ${resData.message || "Lỗi chưa rõ"}`);
                                if (response.status === 401 || response.status === 403 || (resData.message && (resData.message.includes("token") || resData.message.includes("Cookie") || resData.message.includes("hết hạn")))) {
                                    writeLog(`🚨 [NGẮT TIẾN TRÌNH] Phát hiện lỗi xác thực (Token/Cookie hết hạn hoặc không hợp lệ). Ngừng cào hàng loạt!`);
                                    isAuthError = true;
                                }
                            }
                        } catch(e) {
                            if (cardBtn) cardBtn.className = "kn-scrape-btn failed";
                            writeLog(`❌ [${i+1}/${checkboxes.length}] Lỗi phản hồi JSON.`);
                        }
                        resolve();
                    },
                    onerror: function() {
                        if (cardBtn) {
                            cardBtn.className = "kn-scrape-btn failed";
                            cardBtn.innerHTML = `❌ Mất kết nối`;
                        }
                        writeLog(`❌ [${i+1}/${checkboxes.length}] Lỗi kết nối server.`);
                        resolve();
                    }
                });
            });
            // Randomized delay between 2 to 5 seconds to prevent rate limiting
            const delayMs = Math.floor(Math.random() * 3000) + 2000;
            writeLog(`Chờ ${(delayMs/1000).toFixed(1)} giây trước khi cào căn tiếp theo...`);
            await new Promise(r => setTimeout(r, delayMs));
        }

        isCrawlingBulk = false;
        if (bulkBtn) bulkBtn.textContent = "Cào các căn đã chọn";
        updateFloatingPanel();
        if (isAuthError) {
            writeLog("🚨 TIẾN TRÌNH CÀO HÀNG LOẠT BỊ NGẮT DO LỖI XÁC THỰC!");
            showToast("Cào hàng loạt bị ngắt do lỗi xác thực!");
        } else {
            writeLog("🏁 HOÀN TẤT TIẾN TRÌNH CÀO HÀNG LOẠT!");
            showToast("Đã hoàn tất cào hàng loạt!");
        }
    }

    let isChecking = false;

    // PARSE DOM TO FIND LISTING CARDS
    async function scanListings() {
        if (isChecking) return;

        // Look for cards: div with class shadow-small
        const cards = document.querySelectorAll('div.shadow-small');
        if (cards.length === 0) {
            detectedListings = [];
            updateFloatingPanel();
            return;
        }

        // Collect detected IDs to batch check their existence
        const detectedIds = [];
        cards.forEach(card => {
            const aTag = card.querySelector('a[href*="/sources/"], a[href*="/Detail/"]');
            if (!aTag) return;
            const href = aTag.getAttribute('href');
            if (!href) return;
            const match = href.match(/\/(?:sources|Detail)\/([a-f0-9\-]{36}|\d+)/i);
            if (match) {
                detectedIds.push(match[1].toLowerCase());
            }
        });

        // Filter out IDs we haven't checked yet and verify their status
        const uncheckedIds = detectedIds.filter(id => !checkedIds.has(id));
        if (uncheckedIds.length > 0) {
            isChecking = true;
            await checkExistLocally(uncheckedIds);
            isChecking = false;
        }

        const currentListings = [];

        cards.forEach(card => {
            // Find detail link
            const aTag = card.querySelector('a[href*="/sources/"], a[href*="/Detail/"]');
            if (!aTag) return;

            const href = aTag.getAttribute('href');
            if (!href) return;
            const match = href.match(/\/(?:sources|Detail)\/([a-f0-9\-]{36}|\d+)/i);
            if (!match) return;

            const tkId = match[1].toLowerCase();

            // Extract title
            const titleEl = card.querySelector('p.line-clamp-2') || card.querySelector('p');
            const title = titleEl ? titleEl.textContent.trim() : 'Không rõ tiêu đề';

            // If button is already injected, update state and skip
            const existingBtn = card.querySelector('.kn-scrape-btn');
            if (existingBtn) {
                if (!existingBtn.classList.contains('crawling')) {
                    const isCrawled = localListingIds.has(tkId);
                    if (isCrawled) {
                        existingBtn.className = 'kn-scrape-btn success';
                        existingBtn.innerHTML = `✅ Đã có`;
                        existingBtn.title = "Căn này đã có trong database local. Nhấn để cào lại.";
                    } else {
                        existingBtn.className = 'kn-scrape-btn';
                        existingBtn.innerHTML = `📥 Cào Căn Này`;
                        existingBtn.title = "Cào căn này về database local.";
                    }
                }
            } else {
                // Create button
                const btn = document.createElement('button');
                const isCrawled = localListingIds.has(tkId);
                if (isCrawled) {
                    btn.className = 'kn-scrape-btn success';
                    btn.innerHTML = `✅ Đã có`;
                    btn.title = "Căn này đã có trong database local. Nhấn để cào lại.";
                } else {
                    btn.className = 'kn-scrape-btn';
                    btn.innerHTML = `📥 Cào Căn Này`;
                    btn.title = "Cào căn này về database local.";
                }
                btn.setAttribute('data-tk-id', tkId);
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    crawlSingle(tkId, btn, title);
                });

                // Append to card
                card.appendChild(btn);
            }

            // Save to current listing array (only unique items)
            if (!currentListings.some(item => item.id === tkId)) {
                currentListings.push({ id: tkId, title: title });
            }
        });

        detectedListings = currentListings;

        // Always update the floating panel checklist to keep counts and checkboxes synchronized with localListingIds
        updateFloatingPanel();
    }

    // RENDER FLOATING PANEL
    function createFloatingPanel() {
        if (document.getElementById('kn-floating-panel')) return;

        const panel = document.createElement('div');
        panel.id = 'kn-floating-panel';
        
        let isCollapsedDefault = false;
        try {
            isCollapsedDefault = localStorage.getItem('kn_panel_collapsed') === 'true';
        } catch (e) {}

        if (isCollapsedDefault) {
            panel.classList.add('collapsed');
        }

        panel.innerHTML = `
            <!-- Collapsed Icon View -->
            <div class="kn-collapsed-icon" title="Mở bảng điều khiển Khang Ngô Scraper">⚡</div>
            
            <!-- Header -->
            <div class="kn-panel-header">
                <div class="kn-panel-title">
                    <span class="logo-dot"></span>
                    Khang Ngô BDS Scraper
                </div>
                <button class="kn-panel-toggle" title="Thu gọn/Mở rộng">✕</button>
            </div>
            
            <!-- Body -->
            <div class="kn-panel-body">
                <div class="kn-stat-row">
                    <span>Số căn phát hiện:</span>
                    <span class="kn-stat-val" id="kn-detected-count">0</span>
                </div>
                
                <!-- Listings Checklist -->
                <div class="kn-listings-list" id="kn-listings-checklist">
                    <div style="padding: 10px; text-align: center; color: rgba(255,255,255,0.4); font-size: 11px;">
                        Chưa phát hiện căn nào...
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="kn-actions-grid">
                    <button class="kn-btn-primary" id="kn-btn-bulk-scrape">Cào các căn đã chọn</button>
                    <button class="kn-btn-secondary" id="kn-btn-sync-cookie">🔑 Đồng bộ Cookie</button>
                    <button class="kn-btn-secondary" id="kn-btn-open-dashboard">🖥️ Dashboard</button>
                </div>
                
                <!-- Config -->
                <div class="kn-config-row" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                        <span class="kn-config-label">Tự động tạo Curation AI:</span>
                        <input type="checkbox" id="kn-run-ai-toggle" style="accent-color: #E31A22; cursor: pointer;" />
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                        <span class="kn-config-label">Cổng Local Server:</span>
                        <input type="text" class="kn-config-input" id="kn-port-input" value="${localPort}" />
                    </div>
                </div>

                <!-- Logs Box -->
                <div class="kn-logs-box" id="kn-logs"></div>
            </div>
        `;

        document.body.appendChild(panel);

        // Bind events
        const header = panel.querySelector('.kn-panel-header');
        const toggleBtn = panel.querySelector('.kn-panel-toggle');
        const collapsedIcon = panel.querySelector('.kn-collapsed-icon');

        const toggleCollapse = () => {
            panel.classList.toggle('collapsed');
            const isCollapsed = panel.classList.contains('collapsed');
            try {
                localStorage.setItem('kn_panel_collapsed', isCollapsed);
            } catch (e) {}
        };

        header.addEventListener('click', toggleCollapse);
        collapsedIcon.addEventListener('click', toggleCollapse);
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleCollapse();
        });

        // Sync Cookie click
        document.getElementById('kn-btn-sync-cookie').addEventListener('click', async () => {
            await syncCookies();
            checkedIds.clear();
            localListingIds.clear();
            detectedListings = [];
            // Re-scan visible listings immediately to update their status and refresh the floating panel
            await scanListings();
            showToast("Đã đồng bộ cookie và quét lại danh sách!");
        });

        // Open Dashboard click
        document.getElementById('kn-btn-open-dashboard').addEventListener('click', () => {
            window.open(getLocalUrl(), '_blank');
        });

        // Bulk Scrape click
        document.getElementById('kn-btn-bulk-scrape').addEventListener('click', () => {
            crawlBulk();
        });

        // AI Curation Toggle change
        const runAiToggle = document.getElementById('kn-run-ai-toggle');
        if (runAiToggle) {
            runAiToggle.checked = runAi;
            runAiToggle.addEventListener('change', (e) => {
                runAi = e.target.checked;
                try {
                    localStorage.setItem('kn_run_ai', runAi);
                } catch (err) {}
                writeLog(`Đã ${runAi ? 'BẬT' : 'TẮT'} tự động tạo Curation AI.`);
            });
        }

        // Port change
        document.getElementById('kn-port-input').addEventListener('change', (e) => {
            localPort = e.target.value.trim() || '5000';
            try {
                localStorage.setItem('kn_scraper_port', localPort);
            } catch (err) {}
            writeLog(`Đổi cổng kết nối sang: ${localPort}`);
        });

        writeLog("Khởi tạo hệ thống Scraper...");
        syncCookies();
    }

    // UPDATE FLOATING PANEL DATA
    function updateFloatingPanel() {
        const countSpan = document.getElementById('kn-detected-count');
        const checklist = document.getElementById('kn-listings-checklist');
        
        // Filter out already crawled listings
        const uncrawledListings = detectedListings.filter(item => !localListingIds.has(item.id));
        
        if (countSpan) {
            countSpan.textContent = uncrawledListings.length;
        }

        if (checklist) {
            if (uncrawledListings.length > 0) {
                checklist.innerHTML = '';
                uncrawledListings.forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'kn-list-item';
                    const isChecked = !uncheckedPanelIds.has(item.id);
                    itemDiv.innerHTML = `
                        <input type="checkbox" class="kn-item-check" value="${item.id}" ${isChecked ? 'checked' : ''} />
                        <span class="kn-item-title" title="${item.title}">${item.title}</span>
                    `;
                    
                    const chk = itemDiv.querySelector('.kn-item-check');
                    if (chk) {
                        chk.addEventListener('change', (e) => {
                            if (e.target.checked) {
                                uncheckedPanelIds.delete(item.id);
                            } else {
                                uncheckedPanelIds.add(item.id);
                            }
                        });
                    }
                    
                    checklist.appendChild(itemDiv);
                });
            } else {
                checklist.innerHTML = `
                    <div style="padding: 10px; text-align: center; color: rgba(255,255,255,0.4); font-size: 11px;">
                        Không phát hiện căn mới nào...
                    </div>
                `;
            }
        }
    }

    // RUN INITIAL ENGINE
    async function runEngine() {
        if (!document.body || !document.head) {
            setTimeout(runEngine, 500);
            return;
        }
        initializeDOM();
        createFloatingPanel();
        
        scanListings();

        // Run scans periodically
        setInterval(scanListings, 1500);
    }

    // Wait until document is ready
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(runEngine, 1000);
    } else {
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(runEngine, 1000);
        });
    }

})();
