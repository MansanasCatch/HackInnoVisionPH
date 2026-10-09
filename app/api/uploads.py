"""Shared helpers for reading multipart uploads."""

from fastapi import HTTPException, UploadFile, status

MAX_TOTAL_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


async def read_uploads(
    files: UploadFile | list[UploadFile] | None,
) -> list[tuple[str, bytes, str | None]]:
    """Read uploaded files into ``(filename, bytes, content_type)`` tuples (25 MB total cap)."""
    uploaded: list[tuple[str, bytes, str | None]] = []
    if not files:
        return uploaded

    total_bytes = 0
    for upload in files if isinstance(files, list) else [files]:
        if upload and upload.filename:
            content = await upload.read()
            total_bytes += len(content)
            if total_bytes > MAX_TOTAL_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Total uploaded files exceed the 25 MB limit.",
                )
            uploaded.append((upload.filename, content, upload.content_type))
    return uploaded
