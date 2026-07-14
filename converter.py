"""HEIC/HEIF -> JPEG/PNG conversion helpers and CLI.

Run directly for batch conversion:
    python converter.py photo1.heic photo2.heic --format jpeg --quality 92
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()
try:
    pillow_heif.register_avif_opener()
except Exception:
    pass


def unique_path(path: Path) -> Path:
    """Return path, or 'name (1).ext' style variant if it already exists."""
    if not path.exists():
        return path
    for i in range(1, 1000):
        candidate = path.with_name(f"{path.stem} ({i}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not find a free name for {path}")


def convert_file(
    src: str | Path,
    fmt: str = "jpeg",
    quality: int = 92,
    out_dir: str | Path | None = None,
) -> Path:
    """Convert one image to JPEG or PNG. Returns the output path."""
    src = Path(src)
    fmt = fmt.lower()
    if fmt not in ("jpeg", "png"):
        raise ValueError(f"Unsupported target format: {fmt}")
    suffix = ".jpg" if fmt == "jpeg" else ".png"

    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        exif = img.info.get("exif")
        icc = img.info.get("icc_profile")

        if fmt == "jpeg" and img.mode not in ("RGB", "L"):
            if "A" in img.mode:  # flatten transparency onto white
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
                img = background
            else:
                img = img.convert("RGB")

        target_dir = Path(out_dir) if out_dir else src.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        out = unique_path(target_dir / (src.stem + suffix))

        save_kwargs = {}
        if exif:
            save_kwargs["exif"] = exif
        if icc:
            save_kwargs["icc_profile"] = icc
        if fmt == "jpeg":
            save_kwargs.update(quality=quality, optimize=True)
        img.save(out, fmt.upper(), **save_kwargs)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert HEIC/HEIF images to JPEG or PNG.")
    parser.add_argument("files", nargs="+", help="Image files to convert")
    parser.add_argument("--format", choices=["jpeg", "png"], default="jpeg")
    parser.add_argument("--quality", type=int, default=92, help="JPEG quality (1-100)")
    parser.add_argument("--outdir", default=None, help="Output directory (default: next to source)")
    args = parser.parse_args(argv)

    failures = 0
    for f in args.files:
        try:
            out = convert_file(f, fmt=args.format, quality=args.quality, out_dir=args.outdir)
            print(f"OK  {f} -> {out}")
        except Exception as e:
            failures += 1
            print(f"FAIL {f}: {e}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
