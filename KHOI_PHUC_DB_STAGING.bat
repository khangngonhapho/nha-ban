@echo off
title Khoi phuc database STAGING - Khang Ngo Nha Pho
color 0E
cd /d "%~dp0"
echo ==================================================================
echo       KHOI PHUC DATABASE STAGING TU GOOGLE SHEETS
echo ==================================================================
echo.
echo [!] Chu y: Day la thiet lap chay cho STAGING (raw_archive_staging.db).
echo.
set STAGING=true
python restore_db_from_sheets.py
echo.
pause
