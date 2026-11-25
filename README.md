# Daymark Desktop

A local-first Windows x64 desktop widget app built on [Rainmeter 4.5.28](https://github.com/rainmeter/rainmeter/releases/tag/v4.5.28.3936). Independent of the Rainmeter project. You can have a clock, system monitor, sticky note and weather card on the desktop **at the same time**. No account, store or separate Rainmeter installation is required.

## I just want the app

1. Run **Daymark-Desktop-1.0-Windows-x64-Setup.exe**. It's a per-user build for Windows 10/11 x64. This independent preview installer is **not code signed**. If your policy requires signed software, build from the source you trust instead; do not disable Windows security features.
2. Open **Daymark Desktop** from Start. The gallery and 12-hour clock appear immediately. Click **Show** on another card; drag its heading to move it. **Hide** takes one card off the desktop without uninstalling it.
3. Try **Edit note** to display your name, choose a gallery accent, or switch the clock to **24h**. **Save layout** remembers arrangements; reopen Daymark from Start to get the gallery back.
4. To practice importing a skin, choose **Install .rmskin → Choose .rmskin file**, select `Examples/Daymark-Today.rmskin` in the app folder, then confirm the preview. Use **Manage skins** for all installed or imported skins. Multiple independent skin folders can be active; two variants of the *same* widget replace one another.

A portable ZIP is also available: **extract the whole folder** somewhere writable and run `Daymark.exe`. Do not run it from inside the ZIP or from Program Files. The installer uses `%LOCALAPPDATA%\Daymark Desktop`. Uninstall from Windows Settings; user skins, notes and layouts are deliberately retained. Old layouts and skins can be backed up locally. Refer to the [offline guide](app/Start%20here.html) for details. This app does not change the global `.rmskin` file association. Use the gallery's importer.

## Default privacy

* The gallery, clock, system stats, notes, fonts and help are local. No accounts, analytics, remote catalog or auto-update checks are enabled. Skin settings turn **both** engine version checks and auto-update off. Install updates manually.
* Opening weather setup is offline. Choosing a city or confirming a custom location sends only the selected coordinates as application data to Open-Meteo over HTTPS; the service sees the IP address and usual HTTP metadata. Polling occurs on load and about every 30 minutes while the live skin is loaded. Custom coordinates are rounded to two decimals. **Disconnect** clears the saved endpoint and stops polling. No geolocation is performed. The included sample skin is offline.
* **Third-party skins are not sandboxed.** A skin can launch programs, load plugins, or access the network under your Windows account. Import only from authors you trust and inspect the installer preview; do not apply a supplied layout unless you want it. Installing skins can restart Rainmeter, so the importer guards against a separate running copy. Network links in the help only open if you click them. Weather data: Open-Meteo, CC BY 4.0; check its terms before commercial use.

## Build and run on Windows (developers only)

Use a **short writable folder** and Windows 10/11 x64. Install Visual Studio **2022** Community or Build Tools with **Desktop development with C++** (MSVC v143 x86/x64, Windows SDK, MSBuild), the **.NET Framework 4.7.1 Developer Pack** (managed upstream plugins), and Python 3.9+ with the Windows launcher. For a setup executable also install **NSIS 3.11+** with the `amd64-unicode` stub. No external Python modules are needed. If the targeting pack is missing, install it rather than silently retargeting plugins.

```bat
py -3 tools\verify.py
"Build Windows.cmd" --run
```

The default entry point copies the engine to a build worktree, builds the actual `Rainmeter.sln` in Release/x64, compiles the Daymark Windows launcher/icon/dialog, includes the starter skins and regenerates the example `.rmskin`. The portable output is `out\Daymark-Desktop\Daymark.exe`. To produce `out\Daymark-Desktop-1.0-Windows-x64-Setup.exe` use `"Build Windows.cmd" --installer`. The full source archive includes the pinned engine so rebuilding does not require a network request once the compiler and SDKs are installed. If using a lean checkout without `upstream/`, explicitly run `py -3 tools\build_windows.py --fetch-upstream --run` to fetch the source archive and verify its SHA-256. A missing or changed dependency is an error, not a reason to fetch an unpinned replacement.

**Build provenance:** stable engine commit [`cbd528813fa72fd48fb946c0e994367ed1aca415`](https://github.com/rainmeter/rainmeter/tree/cbd528813fa72fd48fb946c0e994367ed1aca415); [build instructions at that revision](https://github.com/rainmeter/rainmeter/blob/cbd528813fa72fd48fb946c0e994367ed1aca415/Docs/Building.md). Do not mix the 5.x master build instructions with this branch. The distributed preview reused the official stable x64 engine binaries, verified using the release asset SHA-256 (`de6e010f8c28882bc28dcd8f319c899f34dfddec51e1e4dd4e7a23f68ebfe14d`); the **new native Daymark launcher** and **NSIS installer** were compiled for x64. Widgets were exercised under Wine, not on a native Windows 10/11 machine. The MSVC rebuild instructions are provided; native MSVC/Windows QA and release signing are still release steps, not claims of this preview.

## Source map and contributions

| Path | Purpose |
| --- | --- |
| `launcher/` | Win32 C launcher, same-install import guard and consent dialog for custom coordinates |
| `app/Skins/Daymark/` | Gallery, clock, system stats, notes, offline weather setup, live weather |
| `app/Rainmeter.ini`, `app/Layouts/` | Offline first-run profile and starter layout |
| `examples/` | Editable source for the separate practice skin |
| `packaging/` | Per-user NSIS installer; preserves user settings on reinstall |
| `tools/` | Windows source build and cross-platform package checks |
| `upstream/` | Pinned Rainmeter source with its own notices and original solution |

To contribute a skin, put it in its own folder and add a Show/Hide row in the local gallery. For a networked skin, provide an offline setup screen, name the service and data sent, require explicit opt-in, and provide a disconnect control. Follow `tools/verify.py` and test a fresh profile. Do not submit real notes, coordinates, local logs or credentials in a pull request. Daymark additions are GPL-2.0-or-later; the upstream engine and bundled components retain their own copyright and licenses. See [LICENSE](LICENSE), [third-party notices](app/Third-party%20notices.txt) and `app/Licenses` (including the Liberation Sans font license).
