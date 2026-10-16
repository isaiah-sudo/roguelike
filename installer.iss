; Inno Setup Script for Crypt of the Necrolord
; Dark Fantasy Deckbuilding Roguelike

#define MyAppName "Crypt of the Necrolord"
#define MyAppVersion "1.4.0"
#define MyAppPublisher "Dark Spire Studio"
#define MyAppURL "https://github.com/isaiah-sudo/rougelike"
#define MyAppUpdatesURL "https://github.com/isaiah-sudo/rougelike/releases"
#define MyAppSupportURL "https://github.com/isaiah-sudo/rougelike/issues"
#define MyAppExeName "CryptOfTheNecrolord.exe"

[Setup]
; Unique App ID (generated GUID for this game - maintained across versions for clean updates)
AppId={{5D87F34A-91C2-4B46-880A-6AEBDC9E746F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppSupportURL}
AppUpdatesURL={#MyAppUpdatesURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=CryptOfTheNecrolord_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog commandline
DisableDirPage=no
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion=1.4.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductVersion=1.4.0.0

; Seamless Upgrade & In-Place Update Configuration
; Detects previous installation location and settings automatically
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes
UsePreviousPrivileges=yes
DirExistsWarning=no

; Automatically close any running instance of the game so files can be updated cleanly without reboot
CloseApplications=yes
CloseApplicationsFilter=*.exe,CryptOfTheNecrolord.exe
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
; Ensure player save files directory is never removed during upgrades or uninstalls
Name: "{app}\saves"; Flags: uninsneveruninstall

[Files]
; Main game executable and dependencies (excludes any saves to prevent overwriting user data)
Source: "dist\CryptOfTheNecrolord\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "saves\*,*.save"
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
