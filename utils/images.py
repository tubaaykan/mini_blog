import io
import mimetypes
import os
import uuid

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

try:
    import magic  # type: ignore
except Exception:  # pragma: no cover
    magic = None


def _detect_mime(file_obj: FileStorage) -> str | None:
    header = file_obj.stream.read(2048)
    file_obj.stream.seek(0)

    if magic:
        try:
            return magic.from_buffer(header, mime=True)
        except Exception:
            pass

    if file_obj.filename:
        guessed, _ = mimetypes.guess_type(file_obj.filename)
        return guessed
    return None


def validate_image(file_obj: FileStorage, allowed_extensions: set[str], allowed_mimes: set[str]):
    if not file_obj or not file_obj.filename:
        return True, None

    filename = secure_filename(file_obj.filename)
    if "." not in filename:
        return False, "Invalid image file name."

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in allowed_extensions:
        return False, "Only jpg, png, gif, and webp images are allowed."

    mime = _detect_mime(file_obj)
    if mime not in allowed_mimes:
        return False, "Uploaded file MIME type is not allowed."

    try:
        img_bytes = file_obj.stream.read()
        file_obj.stream.seek(0)
        with Image.open(io.BytesIO(img_bytes)) as image:
            image.verify()
    except Exception:
        file_obj.stream.seek(0)
        return False, "Uploaded file is not a valid image."

    return True, None


def save_image(file_obj: FileStorage, upload_dir: str) -> str:
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = secure_filename(file_obj.filename)
    extension = safe_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    save_path = os.path.join(upload_dir, filename)

    file_obj.save(save_path)
    optimize_image(save_path)
    return filename


def optimize_image(path: str):
    with Image.open(path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(path, optimize=True, quality=85)


def generate_thumbnail(upload_dir: str, filename: str, thumb_dir: str, size=(320, 320)) -> str | None:
    if not filename:
        return None

    source = os.path.join(upload_dir, filename)
    if not os.path.exists(source):
        return None

    os.makedirs(thumb_dir, exist_ok=True)
    thumb_filename = f"thumb_{filename}"
    thumb_path = os.path.join(thumb_dir, thumb_filename)

    with Image.open(source) as image:
        image.thumbnail(size)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(thumb_path, optimize=True, quality=80)

    return thumb_filename
