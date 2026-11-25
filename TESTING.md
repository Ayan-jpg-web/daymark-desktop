# Preview checks

Tested in a temporary Linux build environment with MinGW-w64, NSIS and a 64-bit Wine desktop, using the SHA-256-verified Rainmeter 4.5.28 release.

- Cross-compiled the Daymark launcher and built the x64 per-user installer.
- Launched the app and confirmed simultaneous windows for the 12-hour clock, gallery, system stats, sticky note and offline weather setup.
- Ran the setup executable with a fresh target in an isolated Wine prefix (exit 0); verified the installed launcher, engine, skin importer, gallery, example package, uninstall entry point and product marker.
- Ran `python tools/verify.py`: validated initial privacy flags, links between variants and gallery, all 1,440 clock minutes, note editing control, weather response fixture and disconnection, and the sample package and footer.
- Only a fixture was used for weather; no real location or live API response was used to certify this build.

Before a production release: do a clean MSVC 2022 rebuild and interactive Windows 10/11 smoke test, including display scaling, multiple monitors, recovery after reboot, and uninstall/reinstall with saved notes. Sign builds before distributing them as a trusted publisher. The preview is unsigned.
