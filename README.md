# HEIC Viewer for Windows

**Open iPhone/Android HEIC photos on Windows for free — no Microsoft Store
codec, no ads, no admin rights.**

Windows can't open `.heic` photos out of the box: Microsoft's HEIF support
requires the paid *HEVC Video Extensions* from the Store. This project
replaces it with a fast, lightweight open-source viewer built on
[libheif](https://github.com/strukturag/libheif) — the same decoder VLC and
Linux use.

![HEIC Viewer showing a phone photo](readme%20images/viewer.png)

## Features

- **Double-click any `.heic` / `.heif` / `.hif` / `.avif`** file to view it
- Also opens JPG / PNG / WebP / GIF / BMP / TIFF — browse a whole folder with the arrow keys
- **Right-click → Convert to JPEG** straight from Explorer (EXIF — date, GPS, camera — preserved)
- Zoom to cursor, pan, rotate, fullscreen, save as JPEG/PNG
- Batch conversion CLI
- Installs **per-user** (HKCU registry only): no admin prompt, fully removed by `uninstall.ps1`
- No telemetry, no network access, ~40 MB on disk

## Install

Requires Windows 10/11 and [Python 3.11+](https://www.python.org/downloads/)
(only to build; the built app is standalone).

```powershell
git clone https://github.com/Vineeth-03-Shenoy/heic_extension.git
cd heic_extension
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.\build.ps1     # produces dist\HEICViewer\HEICViewer.exe
.\install.ps1   # registers the .heic/.heif file associations
```

### Make it the default app (one-time click)

Windows 11 protects default-app choices, so the last step is manual:
right-click any `.heic` photo → **Open with** → **Choose another app**:

![Open with menu](readme%20images/open-with-menu.png)

Pick **HEICViewer** and hit **Always**:

![Set default dialog](readme%20images/set-default-dialog.png)

Done — HEIC photos now open on double-click, forever.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| ← / → (or Backspace / Space) | previous / next image in folder |
| Mouse wheel, `+` / `-` | zoom (around cursor) |
| `F` or `0` | fit to window |
| `1` | actual size (100%) |
| Double-click | toggle fit / 100% |
| `R` / `Shift+R` | rotate right / left |
| `Ctrl+S` | save as JPEG/PNG |
| `Ctrl+O` | open file |
| `F11` | fullscreen |
| `Esc` | leave fullscreen / quit |

## Batch conversion

```powershell
# with the built exe (silent):
dist\HEICViewer\HEICViewer.exe --convert photo1.heic photo2.heic

# from source, with options:
.venv\Scripts\python converter.py *.heic --format png --quality 95 --outdir converted
```

## Uninstall

```powershell
.\uninstall.ps1   # removes all registry entries
```

Then delete the folder. Nothing else is left behind.

## Limitations

- This is a viewer + converter, not a system codec: **Explorer thumbnails**
  and the Photos app still won't preview HEIC (that requires a WIC codec — a
  signed C++/COM component).
- HEVC **videos** (iPhone `.mov`/`.mp4`) are out of scope — install
  [VLC](https://www.videolan.org/) (free), which ships its own HEVC decoder.

## How it works

A ~300-line tkinter viewer ([`heic_viewer.py`](heic_viewer.py)) decodes images
through [pillow-heif](https://github.com/bigcat88/pillow_heif)/libheif and
renders only the visible viewport, so even 48 MP photos pan and zoom smoothly.
[`install.ps1`](install.ps1) registers a ProgID and file associations under
`HKCU\Software\Classes` — per-user, no admin, reversible.

## License

[GPL-3.0](LICENSE). The built exe bundles the libheif, libde265 (LGPL-3.0)
and x265 (GPL-2.0+) codecs — see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.
