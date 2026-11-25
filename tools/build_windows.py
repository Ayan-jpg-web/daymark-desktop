"""Build the pinned Rainmeter solution and the Daymark x64 UI. Python 3.9+, stdlib only."""
import argparse, configparser, hashlib, io, os, shutil, struct, subprocess, tempfile, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
UP = ROOT / 'upstream'
VERSION = '4.5.28.3936'
REV = 'cbd528813fa72fd48fb946c0e994367ed1aca415'
URL = 'https://codeload.github.com/rainmeter/rainmeter/legacy.zip/refs/tags/v4.5.28.3936'
DIGEST = '950f51751471d81ec9aa44ecbb4ad53549beb88a77dfe5017fd0c95439b9eb9b'

def acquire(allow=False):
    if (UP/'Rainmeter.sln').is_file(): return
    if not allow: raise SystemExit('Missing upstream/Rainmeter.sln. Use the complete source ZIP, or explicitly pass --fetch-upstream to fetch and verify the pinned dependency.')
    if UP.exists() and any(UP.iterdir()): raise SystemExit('Refusing to overwrite a non-empty upstream directory.')
    from urllib.request import urlopen
    with urlopen(URL, timeout=45) as r: body = r.read(16*1024*1024+1)
    if hashlib.sha256(body).hexdigest() != DIGEST: raise SystemExit('Source ZIP checksum mismatch; nothing was installed.')
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        for item in archive.infolist():
            path=PurePosixPath(item.filename); parts=path.parts
            if not parts or not parts[0].endswith(REV[:7]) or '..' in parts or path.is_absolute() or '\\' in item.filename or ':' in item.filename: raise ValueError('Unexpected archive path')
        for item in archive.infolist():
            path=UP.joinpath(*PurePosixPath(item.filename).parts[1:]);
            if item.is_dir(): path.mkdir(parents=True,exist_ok=True); continue
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(archive.read(item))

def pack_example(out):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'examples').rglob('*')):
            if p.is_file():
                rel=p.relative_to(ROOT/'examples').as_posix(); z.write(p,rel if rel=='RMSKIN.ini' else 'Skins/'+rel)
    data=buf.getvalue(); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data+struct.pack('<qB7s',len(data),0,b'RMSKIN\0'))

def vsenv():
    env=os.environ.copy(); env['VSCMD_SKIP_SENDTELEMETRY']='1'; env['DOTNET_CLI_TELEMETRY_OPTOUT']='1'
    if (env.get('VSCMD_ARG_TGT_ARCH') or '').lower() in ('x64','amd64') and shutil.which('cl.exe') and shutil.which('msbuild.exe'): return env
    finder=Path(env.get('ProgramFiles(x86)',''))/'Microsoft Visual Studio/Installer/vswhere.exe'
    if not finder.is_file(): raise SystemExit('Install Visual Studio 2022 with Desktop development with C++ (v143) and the .NET Framework 4.7.1 Developer Pack.')
    result=subprocess.check_output([str(finder),'-latest','-version','[17.0,18.0)','-products','*','-requires','Microsoft.VisualStudio.Component.VC.Tools.x86.x64','-property','installationPath','-utf8']).decode('utf-8-sig').strip()
    vc=Path(result)/'VC/Auxiliary/Build/vcvarsall.bat'
    if not result or not vc.is_file(): raise SystemExit('No VS 2022 C++ x64 toolchain found. Modify the Visual Studio installation first.')
    env['DAYMARK_VCENV']=str(vc)
    command=r'cmd.exe /d /u /s /c "call "%DAYMARK_VCENV%" x64 >nul && set"'
    settings=subprocess.check_output(command,env=env).decode('utf-16-le').splitlines()
    env.update({k.upper():v for k,v in (line.split('=',1) for line in settings if '=' in line and not line.startswith('='))})
    return env

def build(args):
    if os.name!='nt': raise SystemExit('Build on 64-bit Windows. Cross-platform checks: python tools/verify.py')
    acquire(args.fetch_upstream); env=vsenv(); out=ROOT/'out'; out.mkdir(exist_ok=True); engine=out/'engine-work'; stage=out/'Daymark-Desktop'; stage.mkdir(exist_ok=True)
    shutil.copytree(UP,engine,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','.vs','x32-*','x64-*'))
    # Upstream normally stamps these files in Build/Build.bat. Only touch the build copy.
    vheader='#pragma once\n#define FILEVER 4,5,28,3936\n#define PRODUCTVER FILEVER\n#define STRFILEVER "4.5.28.3936"\n#define STRPRODUCTVER STRFILEVER\n#define APPVERSION L"4.5.28"\n#define RAINMETER_VERSION 4005028\n#define STRCOPYRIGHT "Rainmeter Team"\n#define BUILD_TIME L"Daymark local build"\n#define COMMIT_HASH L"'+REV+'"\nconst int revision_number=3936;\n'
    (engine/'Version.h').write_text(vheader,encoding='ascii'); (engine/'Version.cs').write_text('namespace Rainmeter { public class Version { public const string Informational = "4.5.28.3936 (64-bit)"; } }',encoding='ascii')
    def go(seq,here):
        exe=shutil.which(seq[0],path=env.get('PATH') or env.get('Path')) or seq[0]; subprocess.run([exe,*map(str,seq[1:])],cwd=here,env=env,check=True)
    buildopts=['/nologo','/m:2','/p:Configuration=Release','/p:Platform=x64','/p:ExcludeTests=true','/p:TrackFileAccess=false']
    go(['msbuild.exe','Rainmeter.sln',*buildopts],engine)
    # Build all matching language resources; do not modify the original Language.rc.
    lang=engine/'Language'; rc=lang/'Language.rc'; old=rc.read_bytes()
    try:
        for row in (lang/'List').read_text(encoding='utf-8-sig').splitlines():
            if not row.strip(): continue
            name,_,lcid=row.strip().split(','); rc.write_text('#include "'+name+'.h"\n#include "Resource.rc"\n',encoding='ascii'); go(['msbuild.exe','Rainmeter.sln','/t:Language',*buildopts,'/p:TargetName='+lcid],engine)
    finally: rc.write_bytes(old)
    b=engine/'x64-Release'
    for nm in ('Rainmeter.exe','Rainmeter.dll','SkinInstaller.exe','RestartRainmeter.exe'): shutil.copy2(b/nm,stage/nm)
    for nm in ('Languages','Plugins'): shutil.copytree(b/nm,stage/nm,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.pdb','*.lib','*.exp','*Example*'))
    shutil.copy2(engine/'Application/Rainmeter.exe.config',stage)
    vis=engine/'Build/VisualElements'; shutil.copy2(vis/'Rainmeter.VisualElementsManifest.xml',stage); (stage/'VisualElements').mkdir(exist_ok=True)
    for img in vis.glob('*.png'): shutil.copy2(img,stage/'VisualElements')
    obj=out/'launcher-work'; obj.mkdir(exist_ok=True); launcher=ROOT/'launcher'
    go(['rc.exe','/nologo','/fo',obj/'Daymark.res','Daymark.rc'],launcher)
    go(['cl.exe','/nologo','/O2','/MT','/utf-8','/Fo'+str(obj/'Daymark.obj'),'/Fe'+str(stage/'Daymark.exe'),launcher/'Daymark.c',obj/'Daymark.res','/link','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','user32.lib','shell32.lib'],obj)
    shutil.copytree(ROOT/'app',stage,dirs_exist_ok=True); shutil.copytree(ROOT/'app/Skins/Daymark',stage/'Defaults/Skins/Daymark',dirs_exist_ok=True); pack_example(stage/'Examples/Daymark-Today.rmskin')
    for exe in ('Daymark.exe','Rainmeter.exe','Rainmeter.dll'):
        data=(stage/exe).read_bytes(); off=struct.unpack_from('<I',data,60)[0]; assert data[:2]==b'MZ' and data[off:off+4]==b'PE\0\0' and struct.unpack_from('<H',data,off+4)[0]==0x8664
    if args.installer:
        nsis=shutil.which('makensis.exe') or next((str(p) for p in (Path(os.getenv('ProgramFiles(x86)',''))/'NSIS/makensis.exe',Path(os.getenv('ProgramFiles',''))/'NSIS/makensis.exe') if p.is_file()),None)
        if not nsis: raise SystemExit('Portable build is ready. Install NSIS 3.11 or newer (with amd64-unicode stub) to build Setup.exe.')
        go([nsis,'/DSTAGE='+str(stage),'/DOUTPUT='+str(out/'Daymark-Desktop-1.0-Windows-x64-Setup.exe'),'Setup.nsi'],ROOT/'packaging')
    print('Built:',stage/'Daymark.exe');
    if args.run: subprocess.Popen([str(stage/'Daymark.exe')],cwd=stage)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--installer',action='store_true'); parser.add_argument('--run',action='store_true'); parser.add_argument('--fetch-upstream',action='store_true',help='Allow fetching the pinned engine archive only if missing.'); build(parser.parse_args())
