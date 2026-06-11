@echo off
title He thong Khoi chay Mini-App Bien tap ro hang Khang Ngo Nha Pho
color 0B
echo ==================================================================
echo       HE THONG KHOI CHAY CO SO DU LIEU LOCALS ^& MINI-APP
echo ==================================================================
echo.
echo [*] Dang khoi dong Local Flask Server...
echo [*] Ung dung se tu dong chay tai: http://localhost:5000
echo.

:: Mo trinh duyet sau 2 giay de server Flask co du thoi gian khoi dong
start /b "" cmd /c "ping 127.0.0.1 -n 3 >nul && start http://localhost:5000"

:: Khoi dong server Flask o terminal hien tai
python manager.py

pause
