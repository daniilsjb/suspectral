[Setup]
AppName=Suspectral
AppVersion=0.0.1
DefaultDirName={commonpf}\Suspectral
DefaultGroupName=Suspectral
UninstallDisplayIcon={app}\Suspectral.exe
Compression=lzma
SolidCompression=yes
OutputDir=..\dist\installer
OutputBaseFilename=SuspectralInstaller
SetupIconFile=..\resources\icons\suspectral.ico
LicenseFile=..\..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\suspectral\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Suspectral"; Filename: "{app}\Suspectral.exe"
Name: "{group}\Uninstall Suspectral"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Suspectral.exe"; Description: "Launch Suspectral"; Flags: nowait postinstall skipifsilent
