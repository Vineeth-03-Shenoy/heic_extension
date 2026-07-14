"""HEIC Viewer — a free, lightweight Windows image viewer with HEIC/HEIF support.

Usage:
    HEICViewer.exe [image]              open the viewer
    HEICViewer.exe --convert FILE...    convert files to JPEG next to the originals (no UI)

Shortcuts:
    Left/Right or Space/Backspace   previous / next image in folder
    Mouse wheel, + / -              zoom (around cursor)
    F or 0                          fit to window
    1                               actual size (100%)
    R / Shift+R                     rotate right / left
    Ctrl+S                          save as JPEG/PNG
    Ctrl+O                          open file
    F11                             fullscreen
    Esc                             leave fullscreen / quit
"""

from __future__ import annotations

import ctypes
import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import pillow_heif
from PIL import Image, ImageOps, ImageTk

import converter

pillow_heif.register_heif_opener()
try:
    pillow_heif.register_avif_opener()
except Exception:
    pass

Image.MAX_IMAGE_PIXELS = None  # trust local files; phones produce 48MP+ HEICs

HEIC_EXTS = {".heic", ".heif", ".hif", ".avif"}
BROWSE_EXTS = HEIC_EXTS | {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}

MIN_ZOOM = 0.02
MAX_ZOOM = 16.0
BG = "#1e1e1e"
BAR_BG = "#2b2b2b"
BAR_FG = "#cccccc"


class ViewerApp:
    def __init__(self, root: tk.Tk, path: Path | None):
        self.root = root
        self.files: list[Path] = []
        self.index = -1
        self.base: Image.Image | None = None   # EXIF-transposed original
        self.rotation = 0                      # extra user rotation, degrees CW
        self.rotated: Image.Image | None = None
        self.zoom: float | None = None         # None = fit to window
        self.offx = 0.0
        self.offy = 0.0
        self.photo: ImageTk.PhotoImage | None = None
        self._drag_start = None
        self._fullscreen = False

        root.title("HEIC Viewer")
        root.configure(bg=BG)
        root.geometry("1200x800")
        try:
            root.state("zoomed")
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0, cursor="fleur")
        self.canvas.pack(fill="both", expand=True)
        self.status = tk.Label(root, text="", anchor="w", bg=BAR_BG, fg=BAR_FG, padx=8)
        self.status.pack(fill="x", side="bottom")

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Double-Button-1>", lambda e: self.toggle_fit_actual(e))

        for key in ("<Left>", "<BackSpace>"):
            root.bind(key, lambda e: self.step(-1))
        for key in ("<Right>", "<space>"):
            root.bind(key, lambda e: self.step(1))
        root.bind("<plus>", lambda e: self.zoom_by(1.25))
        root.bind("<equal>", lambda e: self.zoom_by(1.25))
        root.bind("<minus>", lambda e: self.zoom_by(0.8))
        root.bind("f", lambda e: self.set_fit())
        root.bind("0", lambda e: self.set_fit())
        root.bind("1", lambda e: self.set_zoom(1.0))
        root.bind("r", lambda e: self.rotate(90))
        root.bind("R", lambda e: self.rotate(-90))
        root.bind("<Control-s>", lambda e: self.save_as())
        root.bind("<Control-o>", lambda e: self.open_dialog())
        root.bind("<F11>", lambda e: self.toggle_fullscreen())
        root.bind("<Escape>", lambda e: self.on_escape())

        if path is None:
            self.open_dialog()
        else:
            self.load_path(path)

    # ---------- file handling ----------

    def open_dialog(self):
        filetypes = [
            ("Images", " ".join(f"*{e}" for e in sorted(BROWSE_EXTS))),
            ("HEIC/HEIF", "*.heic *.heif *.hif *.avif"),
            ("All files", "*.*"),
        ]
        name = filedialog.askopenfilename(title="Open image", filetypes=filetypes)
        if name:
            self.load_path(Path(name))

    def load_path(self, path: Path):
        path = path.resolve()
        folder = path.parent
        self.files = sorted(
            (p for p in folder.iterdir() if p.suffix.lower() in BROWSE_EXTS and p.is_file()),
            key=lambda p: p.name.lower(),
        )
        try:
            self.index = self.files.index(path)
        except ValueError:
            self.files = [path]
            self.index = 0
        self.load_current()

    def load_current(self):
        path = self.files[self.index]
        try:
            with Image.open(path) as img:
                img.load()
                self.base = ImageOps.exif_transpose(img)
        except Exception as e:
            messagebox.showerror("HEIC Viewer", f"Could not open {path.name}:\n{e}")
            self.base = None
            self.update_status(error=str(e))
            return
        self.rotation = 0
        self.rotated = None
        self.zoom = None
        self.offx = self.offy = 0.0
        self.root.title(f"{path.name} — HEIC Viewer")
        self.redraw()

    def step(self, delta: int):
        if not self.files:
            return
        self.index = (self.index + delta) % len(self.files)
        self.load_current()

    # ---------- transforms ----------

    def current_image(self) -> Image.Image | None:
        if self.base is None:
            return None
        if self.rotation == 0:
            return self.base
        if self.rotated is None:
            self.rotated = self.base.rotate(-self.rotation, expand=True)
        return self.rotated

    def rotate(self, degrees: int):
        self.rotation = (self.rotation + degrees) % 360
        self.rotated = None
        self.zoom = None
        self.offx = self.offy = 0.0
        self.redraw()

    def fit_zoom(self, img: Image.Image) -> float:
        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        return min(cw / img.width, ch / img.height, 1.0)

    def effective_zoom(self, img: Image.Image) -> float:
        return self.zoom if self.zoom is not None else self.fit_zoom(img)

    def set_fit(self):
        self.zoom = None
        self.offx = self.offy = 0.0
        self.redraw()

    def set_zoom(self, z: float, cursor=None):
        img = self.current_image()
        if img is None:
            return
        old = self.effective_zoom(img)
        z = max(MIN_ZOOM, min(MAX_ZOOM, z))
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        px = cursor[0] if cursor else cw / 2
        py = cursor[1] if cursor else ch / 2
        # keep the image point under (px, py) stationary while zooming
        x0 = (cw - img.width * old) / 2 + self.offx
        y0 = (ch - img.height * old) / 2 + self.offy
        u = (px - x0) / old
        v = (py - y0) / old
        self.zoom = z
        self.offx = px - u * z - (cw - img.width * z) / 2
        self.offy = py - v * z - (ch - img.height * z) / 2
        self.redraw()

    def zoom_by(self, factor: float, cursor=None):
        img = self.current_image()
        if img is None:
            return
        self.set_zoom(self.effective_zoom(img) * factor, cursor=cursor)

    def toggle_fit_actual(self, event):
        if self.zoom is None:
            self.set_zoom(1.0, cursor=(event.x, event.y))
        else:
            self.set_fit()

    # ---------- events ----------

    def on_wheel(self, event):
        self.zoom_by(1.25 if event.delta > 0 else 0.8, cursor=(event.x, event.y))

    def on_drag_start(self, event):
        self._drag_start = (event.x, event.y, self.offx, self.offy)

    def on_drag_move(self, event):
        if self._drag_start is None:
            return
        sx, sy, ox, oy = self._drag_start
        self.offx = ox + (event.x - sx)
        self.offy = oy + (event.y - sy)
        self.redraw()

    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)

    def on_escape(self):
        if self._fullscreen:
            self.toggle_fullscreen()
        else:
            self.root.destroy()

    # ---------- rendering ----------

    def redraw(self):
        self.canvas.delete("all")
        img = self.current_image()
        if img is None:
            return
        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        z = self.effective_zoom(img)
        dw, dh = img.width * z, img.height * z

        # clamp panning so the image can't be dragged fully off-screen
        max_off_x = max((dw - cw) / 2, 0) + cw / 3
        max_off_y = max((dh - ch) / 2, 0) + ch / 3
        self.offx = max(-max_off_x, min(max_off_x, self.offx))
        self.offy = max(-max_off_y, min(max_off_y, self.offy))

        x0 = (cw - dw) / 2 + self.offx
        y0 = (ch - dh) / 2 + self.offy

        # render only the visible part of the image (memory-safe at high zoom)
        sx1 = max(0.0, -x0 / z)
        sy1 = max(0.0, -y0 / z)
        sx2 = min(float(img.width), (cw - x0) / z)
        sy2 = min(float(img.height), (ch - y0) / z)
        if sx2 <= sx1 or sy2 <= sy1:
            self.update_status()
            return
        box = (math.floor(sx1), math.floor(sy1), math.ceil(sx2), math.ceil(sy2))
        crop = img.crop(box)
        tw = max(1, round(crop.width * z))
        th = max(1, round(crop.height * z))
        resample = Image.Resampling.LANCZOS if z < 1 else Image.Resampling.NEAREST
        if z != 1:
            crop = crop.resize((tw, th), resample)
        self.photo = ImageTk.PhotoImage(crop)
        self.canvas.create_image(x0 + box[0] * z, y0 + box[1] * z, image=self.photo, anchor="nw")
        self.update_status()

    def update_status(self, error: str | None = None):
        if not self.files:
            self.status.config(text="No image")
            return
        path = self.files[self.index]
        if error or self.base is None:
            self.status.config(text=f"{path.name}  —  failed to load: {error}")
            return
        img = self.current_image()
        z = self.effective_zoom(img)
        fit = " (fit)" if self.zoom is None else ""
        self.status.config(
            text=f"{path.name}   {self.index + 1}/{len(self.files)}   "
            f"{img.width}×{img.height}   {z * 100:.0f}%{fit}"
        )

    # ---------- actions ----------

    def save_as(self):
        img = self.current_image()
        if img is None:
            return
        src = self.files[self.index]
        name = filedialog.asksaveasfilename(
            title="Save as",
            initialfile=src.stem + ".jpg",
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")],
        )
        if not name:
            return
        out = Path(name)
        try:
            to_save = img
            if out.suffix.lower() in (".jpg", ".jpeg") and to_save.mode not in ("RGB", "L"):
                to_save = to_save.convert("RGB")
            kwargs = {"quality": 92, "optimize": True} if out.suffix.lower() in (".jpg", ".jpeg") else {}
            exif = self.base.info.get("exif") if self.rotation == 0 else None
            if exif:
                kwargs["exif"] = exif
            to_save.save(out, **kwargs)
            self.status.config(text=f"Saved {out}")
        except Exception as e:
            messagebox.showerror("HEIC Viewer", f"Could not save:\n{e}")


def run_convert(files: list[str]) -> int:
    """Silent conversion mode used by the Explorer context menu."""
    errors = []
    for f in files:
        try:
            converter.convert_file(f)
        except Exception as e:
            errors.append(f"{Path(f).name}: {e}")
    if errors:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("HEIC Viewer", "Conversion failed:\n" + "\n".join(errors))
        root.destroy()
        return 1
    return 0


def main() -> int:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    args = sys.argv[1:]
    if args and args[0] == "--convert":
        return run_convert(args[1:])

    path = Path(args[0]) if args else None
    if path is not None and not path.exists():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("HEIC Viewer", f"File not found:\n{path}")
        return 1

    root = tk.Tk()
    ViewerApp(root, path)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
