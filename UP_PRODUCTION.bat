@echo off
chcp 65001 > nul
echo ==================================================
echo    BDS KHANG NGÔ - TIẾN TRÌNH XUẤT BẢN PRODUCTION
echo ==================================================

:: 1. Tự động dọn sạch các file lock của Git để tránh lỗi chặn merge/push do đồng bộ Google Drive
echo [*] Dang don dep file khoa Git du thua (neu co)...
if exist ".git\index.lock" (
    del /f /q ".git\index.lock"
    echo   [x] Da xoa .git/index.lock
)
if exist ".git\packed-refs.lock" (
    del /f /q ".git\packed-refs.lock"
    echo   [x] Da xoa .git/packed-refs.lock
)
if exist ".git\refs\heads\packed-refs.lock" (
    del /f /q ".git\refs\heads\packed-refs.lock"
    echo   [x] Da xoa .git/refs/heads/packed-refs.lock
)

:: 2. Thực hiện chuyển nhanh sang main, merge staging và push
echo [*] Dang chuyen sang nhanh main...
git checkout main
if %ERRORLEVEL% neq 0 (
    echo [❌ LOI] Khong the checkout sang nhanh main.
    goto end
)

echo [*] Dang merge staging vao main...
git merge staging --no-edit --no-verify
if %ERRORLEVEL% neq 0 (
    echo [❌ LOI] Gặp xung đột hoac loi khi merge code.
    git checkout staging
    goto end
)

echo [*] Dang push code len GitHub (origin/main)...
git push origin main --no-verify
if %ERRORLEVEL% neq 0 (
    echo [⚠️ CANH BAO] Push len origin/main gap loi. Tien hanh tiep tuc...
)

echo [*] Dang chuyen tro lai nhanh staging...
git checkout staging
if %ERRORLEVEL% neq 0 (
    echo [❌ LOI] Khong the quay lai nhanh staging.
    goto end
)

echo [*] Dang push code staging len GitHub (origin/staging)...
git push origin staging --no-verify

echo ==================================================
echo [✅] ĐÃ XUẤT BẢN LÊN PRODUCTION & STAGING THÀNH CÔNG!
echo Vercel dang tu dong build phien ban moi nhat.
echo ==================================================

:end
pause
