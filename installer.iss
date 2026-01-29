[Setup]
AppName=Story Lord
AppId={{8B306052-16FA-45C6-B320-A081822EC70F}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Story Lord
DefaultGroupName=Story Lord
OutputDir=bin\Installer
OutputBaseFilename={#OutputFileName}
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupMutex=StoryLordSetupMutex
AppMutex=StoryLordAppMutex

[Files]
; Source is the OUTPUT of PyInstaller (directory mode)
; Expects SourceDir to be defined via command line /DSourceDir="..."
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Story Lord"; Filename: "{app}\StoryLord.exe"
[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}')

[Run]
Filename: "{app}\StoryLord.exe"; Description: "{cm:LaunchProgram,Story Lord}"; Flags: nowait postinstall skipifsilent runasoriginaluser

[Code]
var
  UninstallConfig: Boolean;
  UninstallStories: Boolean;

function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  // look for the path with leading and trailing semicolon
  // Pos() returns 0 if not found
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  // Pre-uninstall selection
  UninstallConfig := False;
  UninstallStories := False;

  if MsgBox('Do you want to remove your Configuration files (~/.storylord)?' #13#10 + 
            '(Selecting "No" will keep your settings for future installs)', mbConfirmation, MB_YESNO) = IDYES then
      UninstallConfig := True;

  if MsgBox('Do you want to remove your Story Data (Documents/StoryLord)?' #13#10 + 
            'WARNING: This cannot be undone!', mbConfirmation, MB_YESNO) = IDYES then
      UninstallStories := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  UserProfile: String;
  ConfigDir: String;
  StoriesDir: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    UserProfile := GetEnv('USERPROFILE');
    ConfigDir := UserProfile + '\.storylord';
    StoriesDir := UserProfile + '\Documents\StoryLord';

    if UninstallConfig then
    begin
        if DirExists(ConfigDir) then
            DelTree(ConfigDir, True, True, True);
    end;

    if UninstallStories then
    begin
        if DirExists(StoriesDir) then
            DelTree(StoriesDir, True, True, True);
    end;
  end;
end;

