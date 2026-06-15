@echo off
title Chay E2E Test headed - Khang Ngo Nha Pho
color 0A
echo ==================================================================
echo         KHOI DONG RUN TEST E2E CU MO PHONG ADMIN (HEADED)
echo ==================================================================
echo.
echo [*] Dang chuan bi moi truong va khoi dong Local server + Google Sheets API mock...
echo [*] Trinh duyet Chrome se hien thi tu dong.
echo [*] Sau khi hoan thanh, trinh duyet se tam dung 120 giay de ban kiem tra.
echo.

python scratch/test_e2e_curation.py --headed

pause
