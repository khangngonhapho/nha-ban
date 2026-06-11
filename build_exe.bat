@echo off
title Bien dich Ung dung Khang Ngo Curator sang EXE
color 0A
echo ==================================================================
echo       TIẾN TRÌNH BIÊN DỊCH ỨNG DỤNG STANDALONE (KHÔNG CẦN PYTHON)
echo ==================================================================
echo.

:: Dam bao thu muc static ton tai de PyInstaller khong bi loi
if not exist static mkdir static

echo [*] Dang bien dich bang PyInstaller...
echo [*] Vui long doi trong giay lat...
echo.

python -c "exec('import dis, PyInstaller.__main__\nold = dis._get_const_info\ndef safe(*a,**k):\n try: return old(*a,**k)\n except: return (None,\"IndexError\")\ndis._get_const_info = safe\nPyInstaller.__main__.run()')" --name "KhangNgoCurator" --onedir --noconfirm --clean --add-data "curator.html;." --add-data "thienkhoi_cookie.txt;." --add-data "static;static" manager.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [❌ LÕI] Bien dich that bai! Vui long kiem tra log tren.
    rem pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==================================================================
echo [✅ HOÀN TẤT THÀNH CÔNG]
echo.
echo Thu muc ung dung chay doc lap da duoc tao tai:
echo    d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\dist\KhangNgoCurator\
echo.
echo File chay chinh:
echo    d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\dist\KhangNgoCurator\KhangNgoCurator.exe
echo.
echo Anh co the copy ca thu muc KhangNgoCurator nay sang may tinh khac 
echo de chay truc tiep ma khong can cai dat Python hay thu vien nao!
echo ==================================================================
echo.
rem pause
