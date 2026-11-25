"""Local-only source/package smoke checks. Usage: python tools/verify.py"""
import configparser, datetime, io, re, struct, tempfile, zipfile
from pathlib import Path
from build_windows import ROOT,pack_example

def read(path):
    b=path.read_bytes(); return b.decode('utf-16' if b[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8-sig')
def cfg(path):
    c=configparser.ConfigParser(interpolation=None,strict=True); c.optionxform=str;c.read_string(read(path));return c

def main():
    app=ROOT/'app'; folder=app/'Skins/Daymark'; live=folder/'Weather/Live.ini'; default=cfg(app/'Rainmeter.ini')
    assert {k for k in default if default[k].get('Active')=='1'}=={r'Daymark\Gallery',r'Daymark\Clock'}
    for p in [app/'Rainmeter.ini',*app.glob('Layouts/*/Rainmeter.ini'),*app.glob('Defaults/Layouts/*/Rainmeter.ini')]:
        c=cfg(p)['Rainmeter']; assert c['DisableVersionCheck']==c['DisableAutoUpdate']=='1'
    state=cfg(folder/'@Resources/WeatherSettings.inc')['Variables']; assert state['WeatherDisabled']=='1' and not state['WeatherURL']
    sections={p:cfg(p) for p in folder.glob('*/*.ini')}; assert {p.parent.name for p in sections}=={'Gallery','Clock','System','Note','Weather'}
    for p,c in sections.items():
        for s in c.sections():
            row=c[s]; m=row.get('Measure','').lower()
            if m=='webparser': assert p==live and row['URL']=='#WeatherURL#' and row['Disabled']=='#WeatherDisabled#'
            if 'MeasureName' in row: assert row['MeasureName'] in c
            if 'MeterStyle' in row: assert row['MeterStyle'] in c
        for group,variant in re.findall(r'!ActivateConfig "Daymark\\([^"\\]+)" "([^"]+)"',read(p)):
            assert (folder/group/variant).is_file(),(p,group,variant)
    gall=sections[folder/'Gallery/Gallery.ini']; assert all('Add'+id in gall and 'Hide'+id in gall for id in ('Clock','System','Note','Weather'))
    assert all('[!DeactivateConfig' in gall['Hide'+id]['LeftMouseUpAction'] for id in ('Clock','System','Note','Weather'))
    date=datetime.datetime(2024,2,29); c=sections[folder/'Clock/12-hour.ini']['LocalTime']; sub=re.fullmatch(r'"(.*?)":"(.*?)"',c['Substitute'])
    for n in range(1440):
        h,m=divmod(n,60); tt=date.replace(hour=h,minute=m).timetuple(); digits=re.sub(sub[1],sub[2],date.replace(hour=h,minute=m).strftime(c['Format'])); assert digits.startswith(f'{h%12 or 12}:{m:02} ')
    assert 'notepad.exe' in sections[folder/'Note/Note.ini']['Edit']['LeftMouseUpAction']
    weather=sections[live]['Current']; pat=weather['RegExp']; assert re.search(pat, '{"current_units":{"temperature_2m":"°C"},"current":{"time":"2026-01-01T08:00","temperature_2m":-1.4}}')[1]=='-1.4'; assert int(weather['UpdateRate'])==1800
    assert 'WeatherDisabled "1"' in sections[live]['Disconnect']['LeftMouseUpAction']
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/'Today.rmskin';pack_example(f); b=f.read_bytes(); assert struct.unpack('<qB7s',b[-16:])==(len(b)-16,0,b'RMSKIN\0')
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            assert z.testzip() is None and 'RMSKIN.ini' in z.namelist() and 'Skins/Daymark Today/Today.ini' in z.namelist()
            if (app/'Examples/Daymark-Today.rmskin').is_file():
                with zipfile.ZipFile(app/'Examples/Daymark-Today.rmskin') as installed:
                    assert set(installed.namelist())==set(z.namelist()) and all(installed.read(n)==z.read(n) for n in z.namelist())
    print('PASS: startup, four independent cards, time formats, note, weather consent & fixture, gallery links and offline import package.')
if __name__=='__main__': main()
