"""Generate assets/heic.ico — app + file-type icon."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = max(1, size // 16)
    r = size // 5
    d.rounded_rectangle([m, m, size - m, size - m], radius=r, fill=(48, 68, 130, 255))

    # mountain + sun photo glyph
    pad = size // 5
    x1, y1, x2, y2 = pad, pad, size - pad, size - pad
    d.rounded_rectangle([x1, y1, x2, y2], radius=max(2, size // 24), fill=(226, 232, 245, 255))
    w, h = x2 - x1, y2 - y1
    d.polygon(
        [(x1, y2), (x1 + w * 0.38, y1 + h * 0.35), (x1 + w * 0.62, y2)],
        fill=(72, 120, 96, 255),
    )
    d.polygon(
        [(x1 + w * 0.45, y2), (x1 + w * 0.72, y1 + h * 0.5), (x2, y2)],
        fill=(96, 150, 118, 255),
    )
    sun_r = max(2, int(w * 0.11))
    cx, cy = int(x1 + w * 0.74), int(y1 + h * 0.24)
    d.ellipse([cx - sun_r, cy - sun_r, cx + sun_r, cy + sun_r], fill=(245, 200, 92, 255))

    if size >= 48:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", int(size * 0.2))
        except OSError:
            font = ImageFont.load_default()
        text = "HEIC"
        bbox = d.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tag_h = int(size * 0.26)
        ty = size - m - tag_h
        d.rounded_rectangle(
            [size // 2 - tw // 2 - size // 16, ty, size // 2 + tw // 2 + size // 16, size - m - size // 24],
            radius=max(2, size // 24),
            fill=(30, 42, 80, 255),
        )
        d.text((size // 2 - tw // 2 - bbox[0], ty + (tag_h - (bbox[3] - bbox[1])) // 2 - bbox[1]),
               text, font=font, fill=(255, 255, 255, 255))
    return img


def main():
    out = Path(__file__).parent / "assets" / "heic.ico"
    out.parent.mkdir(exist_ok=True)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [draw_icon(s) for s in sizes]
    images[-1].save(out, format="ICO", append_images=images[:-1],
                    sizes=[(s, s) for s in sizes])
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
