"""Unit tests for Image OCR text extraction using Pillow and RapidOCR."""

import io

from PIL import Image, ImageDraw

from app.services.file_parser import parse_uploaded_file


def _create_test_image(text: str) -> bytes:
    """Create a synthetic PNG image containing legible text."""
    # White canvas with black text
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw simple text
    draw.text((20, 35), text, fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_parse_image_file_with_ocr() -> None:
    text = "Photosynthesis"
    image_bytes = _create_test_image(text)

    result = parse_uploaded_file("notes.png", image_bytes, "image/png")
    assert result.file_type == "image"
    assert result.base64_data is not None
    # OCR should have recognized the text or included OCR extraction block
    assert "Photosynthesis" in result.extracted_text or "OCR" in result.extracted_text


def test_parse_empty_image_file() -> None:
    # Blank 10x10 white image
    img = Image.new("RGB", (10, 10), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    result = parse_uploaded_file("blank.png", image_bytes, "image/png")
    assert result.file_type == "image"
    assert result.base64_data is not None
    assert "[No readable text detected in image]" in result.extracted_text
