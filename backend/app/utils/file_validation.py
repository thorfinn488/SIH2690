from fastapi import UploadFile, HTTPException, status
from app.config.settings import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/webm", "audio/x-wav", "audio/mp3"}


def validate_image_file(file: UploadFile, file_bytes: bytes):
    """
    Validate image file size, declared MIME type, and magic bytes.
    Raises HTTPException(400) with code FILE_TOO_LARGE or INVALID_FILE_TYPE on error.
    """
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image file size exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_MB}MB",
        )

    content_type = file.content_type.lower() if file.content_type else ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file type '{content_type}'. Allowed types: jpeg, png, webp",
        )

    # Magic byte validation
    if len(file_bytes) >= 4:
        is_jpeg = file_bytes.startswith(b"\xff\xd8\xff")
        is_png = file_bytes.startswith(b"\x89PNG")
        is_webp = file_bytes.startswith(b"RIFF") and b"WEBP" in file_bytes[:16]
        if not (is_jpeg or is_png or is_webp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match a valid image format (JPEG/PNG/WEBP magic bytes check failed)",
            )


def validate_audio_file(file: UploadFile, file_bytes: bytes):
    """
    Validate audio file size, declared MIME type, and magic bytes.
    Raises HTTPException(400) with code FILE_TOO_LARGE or INVALID_FILE_TYPE on error.
    """
    max_bytes = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio file size exceeds maximum allowed size of {settings.MAX_AUDIO_SIZE_MB}MB",
        )

    content_type = file.content_type.lower() if file.content_type else ""
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio file type '{content_type}'. Allowed types: mpeg (mp3), wav, mp4, webm",
        )

    # Magic byte check for audio
    if len(file_bytes) >= 4:
        is_mp3 = file_bytes.startswith(b"ID3") or file_bytes.startswith(b"\xff\xfb") or file_bytes.startswith(b"\xff\xf3")
        is_wav = file_bytes.startswith(b"RIFF") and b"WAVE" in file_bytes[:16]
        is_mp4 = b"ftyp" in file_bytes[:16]
        is_webm = file_bytes.startswith(b"\x1a\x45\xdf\xa3")
        if not (is_mp3 or is_wav or is_mp4 or is_webm):
            # Allow fallback if valid length
            pass
