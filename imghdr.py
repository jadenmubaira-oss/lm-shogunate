"""Compatibility shim for Python environments missing stdlib `imghdr`.
This provides a minimal `what()` that uses Pillow to detect image format.
It aims to satisfy imports like `import imghdr` from third-party libs.
"""
from __future__ import annotations

from typing import Optional

try:
    from PIL import Image
except Exception:  # Pillow may not be installed yet
    Image = None


def what(file, h: Optional[bytes] = None) -> Optional[str]:
    """Return a string describing the image type (same names as stdlib imghdr),
    or None if not recognized.

    - If `h` (header bytes) is provided, use that.
    - Otherwise `file` may be a filename, a file-like object, or bytes.
    """
    if Image is None:
        return None

    try:
        if h is not None:
            from io import BytesIO

            img = Image.open(BytesIO(h))
        else:
            # file can be bytes/bytearray, a path, or a file-like object
            if isinstance(file, (bytes, bytearray)):
                from io import BytesIO

                img = Image.open(BytesIO(file))
            else:
                # let Pillow handle path or file-like objects
                img = Image.open(file)

        fmt = getattr(img, "format", None)
        if not fmt:
            return None
        fmt = fmt.lower()
        # Pillow formats map nicely to imghdr names for common types
        mapping = {
            "jpeg": "jpeg",
            "png": "png",
            "gif": "gif",
            "bmp": "bmp",
            "tiff": "tiff",
            "webp": "webp",
            "ico": "ico",
        }
        return mapping.get(fmt, fmt)
    except Exception:
        return None


# Provide the small convenience API the stdlib imghdr exposes
tests = None
