@echo off
echo [*] Dang bien dich KhangNgoCuratorApp sang file EXE duy nhat...
python -c "exec('import dis, PyInstaller.__main__\nold = dis._get_const_info\ndef safe(*a,**k):\n try: return old(*a,**k)\n except: return (None,\"IndexError\")\ndis._get_const_info = safe\nPyInstaller.__main__.run()')" KhangNgoCuratorApp.spec --clean --noconfirm
echo [✅] Da hoàn tat!
