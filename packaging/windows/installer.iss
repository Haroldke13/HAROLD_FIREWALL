; Inno Setup script: builds HAROLD_FIREWALL-Setup.exe from dist\HAROLD_FIREWALL.exe
[Setup]
AppName=HAROLD_FIREWALL
AppPublisher=Harold IT Data
AppPublisherURL=https://harolditdata.uk
AppVersion=1.0.0
DefaultDirName={autopf}\HAROLD_FIREWALL
DefaultGroupName=HAROLD_FIREWALL
OutputBaseFilename=HAROLD_FIREWALL-Setup
OutputDir=..\..\dist
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "..\..\dist\HAROLD_FIREWALL.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\HAROLD_FIREWALL"; Filename: "{app}\HAROLD_FIREWALL.exe"
Name: "{autodesktop}\HAROLD_FIREWALL"; Filename: "{app}\HAROLD_FIREWALL.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\HAROLD_FIREWALL.exe"; Description: "Launch HAROLD_FIREWALL"; Flags: nowait postinstall skipifsilent
