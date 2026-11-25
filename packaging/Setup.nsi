; SPDX-License-Identifier: GPL-2.0-or-later
Unicode true
Target amd64-unicode
RequestExecutionLevel user
SetCompressor /SOLID lzma
!include "MUI2.nsh"
!include "LogicLib.nsh"
!ifndef STAGE
 !error "Pass /DSTAGE=<absolute folder containing Daymark.exe>"
!endif
!ifndef OUTPUT
 !error "Pass /DOUTPUT=<full installer path>"
!endif
Name "Daymark Desktop"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Daymark Desktop"
ShowInstDetails show
ShowUninstDetails show
VIProductVersion 1.0.0.0
VIAddVersionKey "ProductName" "Daymark Desktop"
VIAddVersionKey "FileDescription" "Daymark Desktop - offline widget gallery setup"
VIAddVersionKey "LegalCopyright" "Daymark contributors; Rainmeter contributors"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"
!define MUI_ICON "..\launcher\Daymark.ico"
!define MUI_UNICON "..\launcher\Daymark.ico"
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Welcome to Daymark Desktop"
!define MUI_WELCOMEPAGE_TEXT "Add several widgets to your desktop and drag them into place. The starter gallery works offline. Weather connects only if you choose a location.$\r$\n$\r$\nSetup installs for your Windows user only. No developer tools, account, or separate Rainmeter installation are needed."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\Daymark.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Open the widget gallery"
!insertmacro MUI_PAGE_FINISH
!define MUI_UNCONFIRMPAGE_TEXT_TOP "This removes the app and its shortcuts. Your skins, notes and saved layouts remain in the installation folder."
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
!define UNKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\DaymarkDesktop"
Function .onInit
 SetShellVarContext current
 IfFileExists "$INSTDIR\Daymark-product.ini" daymark
 IfFileExists "$INSTDIR\*.*" other okay
 other:
 MessageBox MB_ICONEXCLAMATION|MB_OK "The Daymark folder already contains files from another installation. Please move that folder before installing. Nothing has been changed." /SD IDOK
 SetErrorLevel 2
 Abort
 daymark:
 IfFileExists "$INSTDIR\Daymark.exe" 0 okay
 ExecWait '"$INSTDIR\Daymark.exe" /running' $0
 StrCmp $0 0 running okay
 running:
 MessageBox MB_OK|MB_ICONINFORMATION "Daymark is open. Right-click its Rainmeter tray icon and choose Exit, then run setup again. Your widgets and notes will be preserved." /SD IDOK
 SetErrorLevel 2
 Abort
 okay:
FunctionEnd
Section "Daymark Desktop"
 SetShellVarContext current
 SetOutPath "$INSTDIR"
 SetOverwrite on
 File "${STAGE}\Daymark.exe"
 File "${STAGE}\Rainmeter.exe"
 File "${STAGE}\Rainmeter.dll"
 File "${STAGE}\Rainmeter.exe.config"
 File "${STAGE}\SkinInstaller.exe"
 File "${STAGE}\RestartRainmeter.exe"
 File "${STAGE}\Rainmeter.VisualElementsManifest.xml"
 File "${STAGE}\Start here.html"
 File "${STAGE}\LICENSE.txt"
 File "${STAGE}\Third-party notices.txt"
 File /r "${STAGE}\VisualElements"
 File /r "${STAGE}\Languages"
 File /r "${STAGE}\Plugins"
 File /r "${STAGE}\Licenses"
 File /r "${STAGE}\Examples"
 File /r "${STAGE}\Defaults"
 ; First install seeds the gallery. Reinstall must not clobber the user's edited skins or settings.
 SetOverwrite off
 File /r "${STAGE}\Skins"
 File /r "${STAGE}\Layouts"
 File "${STAGE}\Rainmeter.ini"
 SetOverwrite on
 WriteINIStr "$INSTDIR\Daymark-product.ini" "Package" "Id" "DaymarkDesktop"
 WriteINIStr "$INSTDIR\Daymark-product.ini" "Package" "Version" "1.0.0"
 WriteUninstaller "$INSTDIR\Uninstall-Daymark.exe"
 CreateDirectory "$SMPROGRAMS\Daymark Desktop"
 CreateShortcut "$SMPROGRAMS\Daymark Desktop\Daymark Desktop.lnk" "$INSTDIR\Daymark.exe"
 CreateShortcut "$SMPROGRAMS\Daymark Desktop\First steps.lnk" "$INSTDIR\Start here.html"
 WriteRegStr HKCU "${UNKEY}" "DisplayName" "Daymark Desktop"
 WriteRegStr HKCU "${UNKEY}" "DisplayVersion" "1.0.0"
 WriteRegStr HKCU "${UNKEY}" "InstallLocation" "$INSTDIR"
 WriteRegStr HKCU "${UNKEY}" "DisplayIcon" "$INSTDIR\Daymark.exe,0"
 WriteRegStr HKCU "${UNKEY}" "UninstallString" '"$INSTDIR\Uninstall-Daymark.exe"'
 WriteRegDWORD HKCU "${UNKEY}" "NoModify" 1
 WriteRegDWORD HKCU "${UNKEY}" "NoRepair" 1
SectionEnd
Section "Uninstall"
 SetShellVarContext current
 ReadINIStr $1 "$INSTDIR\Daymark-product.ini" "Package" "Id"
 StrCmp $1 "DaymarkDesktop" known
 SetErrorLevel 2
 Abort
 known:
 IfFileExists "$INSTDIR\Daymark.exe" 0 stopped
 ExecWait '"$INSTDIR\Daymark.exe" /running' $0
 StrCmp $0 0 0 stopped
 MessageBox MB_OK|MB_ICONINFORMATION "Please exit Daymark from the Rainmeter tray menu first. Your personal files are kept." /SD IDOK
 SetErrorLevel 2
 Abort
 stopped:
 !include "RemoveRuntime.nsh"
 Delete "$SMPROGRAMS\Daymark Desktop\Daymark Desktop.lnk"
 Delete "$SMPROGRAMS\Daymark Desktop\First steps.lnk"
 RMDir "$SMPROGRAMS\Daymark Desktop"
 DeleteRegKey HKCU "${UNKEY}"
 Delete "$INSTDIR\Uninstall-Daymark.exe"
 ; Keep the product marker so a later reinstall can reuse the preserved user files.
SectionEnd
