/* SPDX-License-Identifier: GPL-2.0-or-later. Daymark's small, offline Windows launcher. */
#define UNICODE
#define _UNICODE
#define _WIN32_WINNT 0x0601
#include <windows.h>
#include <shellapi.h>
#include <strsafe.h>
#include <wchar.h>
#include <stdlib.h>
#include "resource.h"
#define CAP 2048
static WCHAR baseDir[CAP], engine[CAP];
static HWND ours; static BOOL another;
static const WCHAR *gallery = L"[!ActivateConfig \"Daymark\\Gallery\" \"Gallery.ini\"][!Show \"Daymark\\Gallery\"]";
static BOOL join(WCHAR *dst, const WCHAR *name) { return SUCCEEDED(StringCchPrintfW(dst,CAP,L"%ls%ls",baseDir,name)); }
static int msg(HWND h,const WCHAR *s){ MessageBoxW(h,s,L"Daymark Desktop",MB_OK|MB_ICONINFORMATION); return 1; }
/* Only inspect the executable path of known Rainmeter control windows. Do not send to another install. */
static BOOL CALLBACK visit(HWND hwnd, LPARAM unused){
 WCHAR cls[100],title[100],path[32768]; DWORD pid=0,n=32768; HANDLE process; (void)unused;
 if(!GetClassNameW(hwnd,cls,100) || wcscmp(cls,L"DummyRainWClass")!=0 || !GetWindowTextW(hwnd,title,100) || wcscmp(title,L"Rainmeter control window")!=0) return TRUE;
 GetWindowThreadProcessId(hwnd,&pid); process=OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,FALSE,pid);
 if(process && QueryFullProcessImageNameW(process,0,path,&n) && !_wcsicmp(path,engine)) ours=hwnd; else another=TRUE;
 if(process)CloseHandle(process); return TRUE;
}
static void findInstances(void){ours=NULL;another=FALSE;EnumWindows(visit,0);}
static BOOL sendLocal(const WCHAR *command){COPYDATASTRUCT data={0}; DWORD_PTR result=0;
 if(!ours)return FALSE;data.dwData=1;data.cbData=(DWORD)((wcslen(command)+1)*sizeof(WCHAR));data.lpData=(void*)command;
 return SendMessageTimeoutW(ours,WM_COPYDATA,0,(LPARAM)&data,SMTO_ABORTIFHUNG,2500,&result)!=0; }
static BOOL runLocal(const WCHAR *name){ WCHAR dest[CAP]; if(!join(dest,name))return FALSE;
 return (INT_PTR)ShellExecuteW(NULL,L"open",dest,NULL,baseDir,SW_SHOWNORMAL)>32; }
static BOOL coord(HWND dlg,int field,double bound,double *result){WCHAR buf[32],*end; size_t i; double value;
 if(!GetDlgItemTextW(dlg,field,buf,32))return FALSE;
 for(i=0;buf[i];++i) if((buf[i]<L'0'||buf[i]>L'9')&&buf[i]!=L'.'&&buf[i]!=L'+'&&buf[i]!=L'-')return FALSE;
 value=wcstod(buf,&end);if(end==buf||*end||value < -bound || value > bound)return FALSE;*result=value;return TRUE; }
static INT_PTR CALLBACK locDlg(HWND dlg,UINT u,WPARAM w,LPARAM arg){ (void)arg;
 if(u==WM_INITDIALOG){SendDlgItemMessageW(dlg,ID_LAT,EM_SETLIMITTEXT,22,0);SendDlgItemMessageW(dlg,ID_LON,EM_SETLIMITTEXT,22,0);SendMessageW(dlg,WM_SETICON,ICON_SMALL,(LPARAM)LoadIconW(GetModuleHandleW(NULL),MAKEINTRESOURCEW(ID_ICON)));return TRUE;}
 if(u==WM_CLOSE||(u==WM_COMMAND&&LOWORD(w)==IDCANCEL)){EndDialog(dlg,0);return TRUE;}
 if(u==WM_COMMAND&&LOWORD(w)==IDOK){ double lat,lon;WCHAR url[400],file[CAP];
  if(!coord(dlg,ID_LAT,90,&lat)||!coord(dlg,ID_LON,180,&lon)){msg(dlg,L"Enter a latitude from -90 to 90 and a longitude from -180 to 180, using a decimal point.");return TRUE;}
  findInstances();if(!ours){msg(dlg,L"Open Daymark Desktop and choose Weather > Set up first.");return TRUE;}
  if(!join(file,L"Skins\\Daymark\\@Resources\\WeatherSettings.inc") || FAILED(StringCchPrintfW(url,400,L"https://api.open-meteo.com/v1/forecast?latitude=%.2f&longitude=%.2f&current=temperature_2m&temperature_unit=celsius",lat,lon))){msg(dlg,L"The installation path is too long.");return TRUE;}
  if(!WritePrivateProfileStringW(L"Variables",L"WeatherCity",L"Custom location",file)||!WritePrivateProfileStringW(L"Variables",L"WeatherURL",url,file)||!WritePrivateProfileStringW(L"Variables",L"WeatherDisabled",L"0",file)){msg(dlg,L"Could not save weather settings. Use a folder you can write to.");return TRUE;}
  if(!sendLocal(L"[!ActivateConfig \"Daymark\\Weather\" \"Live.ini\"]")){msg(dlg,L"Settings saved, but Daymark is not responding. Reopen it to continue.");}
  EndDialog(dlg,1);return TRUE;
 }return FALSE;
}
int WINAPI wWinMain(HINSTANCE inst,HINSTANCE prev,LPWSTR command,int show){DWORD n;WCHAR *sep, profile[CAP];int i; (void)prev;(void)show;
 SetDllDirectoryW(L""); n=GetModuleFileNameW(NULL,baseDir,CAP);if(!n||n>=CAP)return 1;
 sep=wcsrchr(baseDir,L'\\');if(!sep)return 1;sep[1]=0;if(!join(engine,L"Rainmeter.exe")||!join(profile,L"Rainmeter.ini"))return 1;findInstances();
 if(!_wcsicmp(command,L"/running")) return ours?0:1;
 if(!_wcsicmp(command,L"/location")){if(!ours)return msg(NULL,L"Open Daymark Desktop first, then choose Weather > Set up.");return DialogBoxParamW(inst,MAKEINTRESOURCEW(ID_LOCATION),NULL,locDlg,0)==-1?1:0;}
 if(!_wcsicmp(command,L"/import")){if(another)return msg(NULL,L"Rainmeter's skin installer may restart its host. Please exit the other Rainmeter copy from its tray icon before importing into Daymark. Your existing skins will not be moved."); return runLocal(L"SkinInstaller.exe")?0:msg(NULL,L"Skin Installer could not be opened. Extract or reinstall the complete app.");}
 if(*command)return 1;
 if(GetFileAttributesW(profile)==INVALID_FILE_ATTRIBUTES){return msg(NULL,L"The local Daymark profile is missing. Extract the entire app to a writable folder, or reinstall it. Daymark did not start an unconfigured Rainmeter.");}
 if(!ours){if(!runLocal(L"Rainmeter.exe"))return msg(NULL,L"Could not start Rainmeter. Extract the full Windows x64 package, not just Daymark.exe.");
 for(i=0; i<52&&!ours; ++i){ Sleep(150);findInstances(); }}
 if(!ours)return msg(NULL,L"Daymark is still starting or the engine could not open. Check the notification area for its icon.");
 return sendLocal(gallery)?0:msg(NULL,L"Daymark is not responding. Try its tray menu, or restart it.");
}
