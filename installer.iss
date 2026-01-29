[Setup]
AppName=Story Lord
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Story Lord
DefaultGroupName=Story Lord
OutputDir=bin\Installer
OutputBaseFilename=StoryLordSetup
Compression=lzma
SolidCompression=yes

[Files]
; Source is the OUTPUT of PyInstaller (directory mode)
; Expects SourceDir to be defined via command line /DSourceDir="..."
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Story Lord"; Filename: "{app}\StoryLord.exe"
[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}')

[Code]
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

function InitializeSetup(): Boolean;
var
  UninsPath: String;
  ResultCode: Integer;
begin
  Result := True;
  // Check if already installed
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1',
    'UninstallString', UninsPath) then
  begin
    // Clean up quotes
    StringChange(UninsPath, '"', '');
    
    if MsgBox('Story Lord is already installed.' #13#10 #13#10 +
              'Click "Yes" to Reinstall / Repair.' #13#10 +
              'Click "No" to Uninstall.', mbConfirmation, MB_YESNO) = IDNO then
    begin
      // Run Uninstaller
      Exec(UninsPath, '', '', SW_SHOW, ewNoWait, ResultCode);
      Result := False; // Abort Setup
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  UserProfile: String;
  ConfigDir: String;
  StoriesDir: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    UserProfile := ExpandConstant('{userprofile}');
    ConfigDir := UserProfile + '\.storylord';
    StoriesDir := UserProfile + '\Documents\StoryLord';

    // Prompt for Config Removal
    if DirExists(ConfigDir) then
    begin
      if MsgBox('Do you want to PERMANENTLY remove your Configuration files?' #13#10 +
                'Location: ' + ConfigDir, mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(ConfigDir, True, True, True);
      end;
    end;

    // Prompt for Story Data Removal
    if DirExists(StoriesDir) then
    begin
      if MsgBox('Do you want to PERMANENTLY remove all Story Data?' #13#10 +
                'WARNING: This cannot be undone.' #13#10 +
                'Location: ' + StoriesDir, mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(StoriesDir, True, True, True);
      end;
    end;
  end;
end;

