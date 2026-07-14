# Third-party notices

HEIC Viewer's own source code is copyright (c) 2026 Vineeth Shenoy and is
released under the GNU GPL-3.0 (see [LICENSE](LICENSE)).

The application depends on, and built binaries bundle, the following
open-source components:

| Component | License | Role |
| --- | --- | --- |
| [Pillow](https://github.com/python-pillow/Pillow) | MIT-CMU (HPND) | image handling |
| [pillow-heif](https://github.com/bigcat88/pillow_heif) | BSD-3-Clause | Python bindings to libheif |
| [libheif](https://github.com/strukturag/libheif) | LGPL-3.0 | HEIF/HEIC container decoding |
| [libde265](https://github.com/strukturag/libde265) | LGPL-3.0 | HEVC (H.265) image decoding |
| [x265](https://bitbucket.org/multicoreware/x265_git) | GPL-2.0-or-later | HEVC encoding (used when saving .heic) |
| [PyInstaller](https://pyinstaller.org) | GPL-2.0-or-later with bootloader exception | exe packaging only |
| Python + tkinter | PSF License | runtime and UI |

Because distributed binaries include x265 (GPL) and libheif/libde265 (LGPL),
the combined binary distribution is licensed under GPL-3.0, which is
compatible with all of the above.

**Patent note:** HEVC/H.265 is covered by patent pools in some jurisdictions.
This project ships only free, open-source decoder implementations (the same
ones used by VLC and Linux distributions) and is provided for personal use
without any patent license or warranty of any kind.
