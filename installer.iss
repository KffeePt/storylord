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

[Code]
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

