@echo off
title He thong Khoi chay Staging - Khang Ngo Nha Pho
color 0E
echo ==================================================================
echo       HE THONG KHOI CHAY CO SO DU LIEU STAGING ^& MINI-APP
echo ==================================================================
echo.
echo [*] Dang thiet lap moi truong STAGING...
set STAGING=true
echo [*] Dang khoi dong Local Flask Server (STAGING)...
echo [*] Ung dung se tu dong chay tai: http://localhost:5001
echo.

:: Tu dong mo trinh duyet den website local (STAGING)
start "" "http://localhost:5001"

:: Tu dong khoi chay background worker (Staging) trong cua so rieng
start "Khang Ngo - Background Worker (Staging)" python background_worker.py

:: Khoi dong server Flask o terminal hien tai voi STAGING=true
python manager.py

pause
