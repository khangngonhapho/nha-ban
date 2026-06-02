; =====================================================================
; INNO SETUP SCRIPT FOR KHANG NGO CURATOR DASHBOARD
; Nén bộ thư mục PyInstaller độc lập thành bộ cài đặt Setup.exe chuyên nghiệp
; =====================================================================

[Setup]
AppId={{5A87B2E3-8E5A-4DFE-8DF3-B078B1D4B5D4}
AppName=Khang Ngô Curator Dashboard
AppVersion=1.0.0
AppPublisher=Khang Ngô Nhà Phố
AppPublisherURL=https://khangngonhapho.github.io/nha-ban/
AppSupportURL=https://khangngonhapho.github.io/nha-ban/
AppUpdatesURL=https://khangngonhapho.github.io/nha-ban/
DefaultDirName={autopf}\KhangNgoCurator
DefaultGroupName=Khang Ngô Curator Dashboard
AllowNoIcons=yes
; Output folder & filename
OutputDir=d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\dist
OutputBaseFilename=Setup_KhangNgo_Curator_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy toàn bộ file đã được PyInstaller build ra ở dist/KhangNgoCurator/
Source: "d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\dist\KhangNgoCurator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Khang Ngô Curator Dashboard"; Filename: "{app}\KhangNgoCurator.exe"
Name: "{group}\{cm:UninstallProgram,Khang Ngô Curator Dashboard}"; Filename: "{uninstaller}"
Name: "{autodesktop}\Khang Ngô Curator Dashboard"; Filename: "{app}\KhangNgoCurator.exe"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,Khang Ngô Curator Dashboard}"; Filename: "{app}\KhangNgoCurator.exe"; Flags: nowait postinstall skipifsilent
