@echo off
title He thong Khoi chay Mini-App Bien tap ro hang Khang Ngo Nha Pho
color 0B
echo ==================================================================
echo       HE THONG KHOI CHAY CO SO DU LIEU LOCALS ^& MINI-APP
echo ==================================================================
echo.
echo [*] Dang khoi dong Local Flask Server...
echo [*] Ung dung se tu dong chay tai: http://localhost:5001
echo.

:: Tu dong mo trinh duyet den website local
start "" "http://localhost:5001"

:: Tu dong khoi chay background worker xu ly AI & di cu anh trong cua so rieng
start "Khang Ngo - Background Worker" python background_worker.py

:: Khoi dong server Flask o terminal hien tai
python manager.py

pause
