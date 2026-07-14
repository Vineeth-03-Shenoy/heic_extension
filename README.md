# HEIC Viewer

A free, lightweight Windows image viewer with **HEIC/HEIF** support — a
replacement for Microsoft's paid HEVC/HEIF Store extensions. Decoding is done
by [libheif](https://github.com/strukturag/libheif) via
[pillow-heif](https://github.com/bigcat88/pillow_heif), so no Store codecs are
needed.

## What it does

- Double-click any `.heic` / `.heif` / `.hif` / `.avif` file to view it
  (also opens JPG/PNG/WebP/etc., so you can browse a whole folder).
- Right-click a HEIC file → **Convert to JPEG** (saved next to the original,
  EXIF preserved).
- Pan, zoom to cursor, rotate, fullscreen, save as JPEG/PNG.
- Installs per-user (HKCU registry only) — **no admin rights**, fully
  reversible with `uninstall.ps1`.

## Install

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.\build.ps1     # produces dist\HEICViewer\HEICViewer.exe
.\install.ps1   # registers the file associations (current user only)
```

If Windows still opens something else by default: right-click a `.heic` file →
**Open with → Choose another app → HEIC Image** → tick **Always**.

## Shortcuts

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

## Batch conversion (CLI)

```powershell
dist\HEICViewer\HEICViewer.exe --convert photo1.heic photo2.heic
# or from source, with more options:
.venv\Scripts\python converter.py *.heic --format png --outdir converted
```

## Uninstall

```powershell
.\uninstall.ps1   # removes the registry entries; then delete this folder
```

## Limitations

This is a viewer + converter, not a system-wide codec: Explorer thumbnails and
the Photos app still won't decode HEIC (that requires a WIC codec — a signed
C++/COM component). Opening, viewing, and converting HEIC files works fully.
