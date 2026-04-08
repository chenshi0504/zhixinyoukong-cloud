; 智信优控 - 云端版（管理平台）Inno Setup 安装脚本
; 使用方法: 先用 PyInstaller 打包 cloud 项目，再用 Inno Setup 编译此脚本

#define MyAppName "智信优控（云端）"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "智信优控团队"
#define MyAppExeName "智信优控.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567892}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName=D:\Download\智信优控_云端
DefaultGroupName={#MyAppName}
OutputDir=..\release
OutputBaseFilename=智信优控_云端_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"

[Files]
; 主程序目录（PyInstaller 输出）
Source: "..\release\智信优控\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
// 安装前检测外部软件
function InitializeSetup(): Boolean;
var
  SumoPath: String;
  CarlaPath: String;
  Msg: String;
begin
  Result := True;
  Msg := '';

  // 检测 SUMO
  if not RegQueryStringValue(HKLM, 'SOFTWARE\DLR\SUMO', 'InstallDir', SumoPath) then
  begin
    if not DirExists('C:\Program Files (x86)\Eclipse\Sumo') then
      Msg := Msg + '• SUMO 未检测到（交通仿真功能需要）' + #13#10;
  end;

  // 检测 CARLA
  if GetEnv('CARLA_ROOT') = '' then
  begin
    if not DirExists('C:\CARLA') then
      Msg := Msg + '• CARLA 未检测到（自动驾驶仿真功能需要）' + #13#10;
  end;

  if Msg <> '' then
  begin
    MsgBox('以下外部软件未检测到，部分功能可能不可用：' + #13#10#13#10 +
           Msg + #13#10 +
           '您可以在安装完成后再安装这些软件。' + #13#10 +
           '软件启动时会自动检测并提示。',
           mbInformation, MB_OK);
  end;
end;
