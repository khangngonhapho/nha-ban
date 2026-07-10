@echo off
title Khoi phuc database PRODUCTION - Khang Ngo Nha Pho
color 0B
cd /d "%~dp0"
echo ==================================================================
echo       KHOI PHUC DATABASE PRODUCTION TU GOOGLE SHEETS
echo ==================================================================
echo.
echo [!] Chu y: Day la thiet lap chay cho PRODUCTION (raw_archive.db).
echo.
set STAGING=false
python restore_db_from_sheets.py
echo.
pause
