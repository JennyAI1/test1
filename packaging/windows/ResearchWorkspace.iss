#define MyAppName "Research Workspace"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "Research Workspace"
#define MyAppExeName "ResearchWorkspaceLauncher.exe"

[Setup]
AppId={{8A87E211-9B4A-45DF-9CD0-EA0D6184707A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\ResearchWorkspace
DefaultGroupName={#MyAppName}
OutputDir=dist-installer
OutputBaseFilename=ResearchWorkspaceInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\ResearchWorkspaceLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\.env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\docker-compose.prod.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\backend\Dockerfile"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "..\..\backend\requirements.txt"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "..\..\backend\app\*"; DestDir: "{app}\backend\app"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\backend\migrations\*"; DestDir: "{app}\backend\migrations"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\backend\scripts\*"; DestDir: "{app}\backend\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\frontend\Dockerfile"; DestDir: "{app}\frontend"; Flags: ignoreversion
Source: "..\..\frontend\package.json"; DestDir: "{app}\frontend"; Flags: ignoreversion
Source: "..\..\frontend\next.config.mjs"; DestDir: "{app}\frontend"; Flags: ignoreversion
Source: "..\..\frontend\app\*"; DestDir: "{app}\frontend\app"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\frontend\components\*"; DestDir: "{app}\frontend\components"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\frontend\lib\*"; DestDir: "{app}\frontend\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\frontend\next-env.d.ts"; DestDir: "{app}\frontend"; Flags: ignoreversion
Source: "..\..\frontend\tsconfig.json"; DestDir: "{app}\frontend"; Flags: ignoreversion

[Icons]
Name: "{group}\Research Workspace (Start)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "up"
Name: "{group}\Research Workspace (Stop)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "down"
Name: "{group}\Research Workspace (Status)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "status"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "up"; Description: "Start Research Workspace now"; Flags: nowait postinstall skipifsilent
