import dis
import PyInstaller.__main__

# Patch dis to prevent PyInstaller index errors on newer python versions
old = dis._get_const_info
def safe(*a,**k):
    try:
        return old(*a,**k)
    except Exception:
        return (None, "IndexError")
dis._get_const_info = safe

# Run PyInstaller
PyInstaller.__main__.run([
    '--name=KhangNgoCurator',
    '--onedir',
    '--noconfirm',
    '--clean',
    '--add-data=curator.html;.',
    '--add-data=thienkhoi_cookie.txt;.',
    '--add-data=static;static',
    'curator_server.py'
])
