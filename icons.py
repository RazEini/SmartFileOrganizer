"""
Icon / thumbnail generation for files and directories shown
in the folder preview grid.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FILE_ICONS = {}

FILE_TYPE_COLORS = {
    ".txt": (56, 189, 248, 255),
    ".py": (250, 204, 21, 255),
    ".jpg": (251, 146, 60, 255),
    ".jpeg": (251, 146, 60, 255),
    ".png": (74, 222, 128, 255),
    ".pdf": (248, 113, 113, 255),
    ".mp3": (244, 114, 182, 255),
    ".mp4": (251, 146, 60, 255),
    ".zip": (168, 85, 247, 255),
    ".rar": (168, 85, 247, 255),
    ".doc": (59, 130, 246, 255),
    ".docx": (59, 130, 246, 255),
    ".xls": (34, 197, 94, 255),
    ".xlsx": (34, 197, 94, 255),
}


def get_file_icon(file_path: Path, size=(56, 56)):
    """
    Creates a simple modern icon/thumbnail for files and directories.
    """

    suffix = file_path.suffix.lower()
    key = ("DIR" if file_path.is_dir() else suffix)

    # Do not cache real image thumbnails by extension.
    # Otherwise every JPG would display the same image.
    cacheable = not (
        suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
        and file_path.is_file()
    )

    if cacheable and key in FILE_ICONS:
        return FILE_ICONS[key]

    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # --------------------------------------------------------
    # DIRECTORY
    # --------------------------------------------------------

    if file_path.is_dir():

        # Shadow
        draw.rounded_rectangle(
            [5, 10, size[0] - 3, size[1] - 3],
            radius=7,
            fill=(15, 23, 42, 80)
        )

        # Folder
        draw.rounded_rectangle(
            [4, 13, size[0] - 4, size[1] - 5],
            radius=7,
            fill=(99, 102, 241, 255)
        )

        draw.rounded_rectangle(
            [7, 7, 27, 18],
            radius=4,
            fill=(129, 140, 248, 255)
        )

        txt = "DIR"

        bbox = draw.textbbox((0, 0), txt, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(
            ((size[0] - w) / 2, (size[1] - h) / 2 + 5),
            txt,
            fill="white",
            font=font
        )

    # --------------------------------------------------------
    # IMAGE THUMBNAIL
    # --------------------------------------------------------

    elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]:

        try:
            im = Image.open(file_path).convert("RGBA")
            im.thumbnail((size[0] - 4, size[1] - 4), Image.LANCZOS)

            thumb = Image.new("RGBA", size, (30, 41, 59, 255))

            x = (size[0] - im.width) // 2
            y = (size[1] - im.height) // 2

            thumb.paste(im, (x, y), im)

            return thumb

        except Exception:
            pass

        color = FILE_TYPE_COLORS.get(
            suffix,
            (148, 163, 184, 255)
        )

        draw.rounded_rectangle(
            [2, 2, size[0] - 2, size[1] - 2],
            radius=9,
            fill=color
        )

    # --------------------------------------------------------
    # NORMAL FILE
    # --------------------------------------------------------

    else:

        color = FILE_TYPE_COLORS.get(
            suffix,
            (100, 116, 139, 255)
        )

        # file background
        draw.rounded_rectangle(
            [3, 3, size[0] - 3, size[1] - 3],
            radius=9,
            fill=color
        )

        # folded corner
        draw.polygon(
            [
                (size[0] - 18, 3),
                (size[0] - 3, 18),
                (size[0] - 18, 18)
            ],
            fill=(255, 255, 255, 110)
        )

        txt = suffix[1:].upper() if suffix else "FILE"

        if len(txt) > 5:
            txt = txt[:5]

        bbox = draw.textbbox((0, 0), txt, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(
            ((size[0] - w) / 2, (size[1] - h) / 2 + 4),
            txt,
            fill="white",
            font=font
        )

    if cacheable:
        FILE_ICONS[key] = img

    return img
