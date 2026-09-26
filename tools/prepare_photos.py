import sys
from pathlib import Path

from PIL import Image, ImageOps

OUTPUT = Path(__file__).resolve().parent.parent / "images" / "photos"
LONG_SIDE = 1600
QUALITY = 82

APERTURE = 33437
EXPOSURE_TIME = 33434
ISO = 34855
FOCAL_LENGTH = 37386


def settings(image):
    exif = image.getexif().get_ifd(0x8769)
    parts = []
    if APERTURE in exif:
        parts.append(f"f/{float(exif[APERTURE]):g}")
    if FOCAL_LENGTH in exif:
        parts.append(f"{float(exif[FOCAL_LENGTH]):g}mm")
    if EXPOSURE_TIME in exif:
        seconds = float(exif[EXPOSURE_TIME])
        parts.append(f"1/{round(1 / seconds)}s" if seconds < 1 else f"{seconds:g}s")
    if ISO in exif:
        parts.append(f"ISO {exif[ISO]}")
    return " · ".join(parts) or "no camera settings found"


def prepare(path):
    original = Image.open(path)
    camera = settings(original)
    image = ImageOps.exif_transpose(original).convert("RGB")
    image.thumbnail((LONG_SIDE, LONG_SIDE))
    shape = "tall" if image.height > image.width else "wide"
    target = OUTPUT / (path.stem.lower().replace(" ", "-") + ".jpg")
    image.save(target, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    size = target.stat().st_size // 1024
    print(f"{target.relative_to(OUTPUT.parent.parent)}  {shape}  {image.width}x{image.height}  {size} KB  {camera}")


def main():
    if len(sys.argv) < 2:
        print("usage: python tools/prepare_photos.py photo1.jpg photo2.jpg ...")
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:]:
        prepare(Path(name))


if __name__ == "__main__":
    main()
