"""Unit tests for document parsing (PDF, Word, Excel, CSV, Image, Text)."""

import io

import openpyxl
from docx import Document  # type: ignore

from app.services.file_parser import parse_uploaded_file


def test_parse_text_file() -> None:
    content = b"Physics Lesson 1: Newton's Laws of Motion"
    result = parse_uploaded_file("notes.txt", content, "text/plain")
    assert result.file_type == "txt"
    assert "Newton's Laws" in result.extracted_text
    assert result.character_count > 0


def test_parse_csv_file() -> None:
    csv_data = b"Subject,Score\nMath,95\nScience,88"
    result = parse_uploaded_file("scores.csv", csv_data, "text/csv")
    assert result.file_type == "csv"
    assert "Math,95" in result.extracted_text


def test_parse_image_file() -> None:
    img_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    result = parse_uploaded_file("diagram.png", img_data, "image/png")
    assert result.file_type == "image"
    assert result.base64_data is not None


def test_parse_docx_file() -> None:
    doc = Document()
    doc.add_paragraph("Biology Chapter 1: Cell Structure")
    buffer = io.BytesIO()
    doc.save(buffer)
    docx_bytes = buffer.getvalue()

    result = parse_uploaded_file("biology.docx", docx_bytes)
    assert result.file_type == "word"
    assert "Cell Structure" in result.extracted_text


def test_parse_excel_file() -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Grades"
    ws.append(["Student", "Grade"])
    ws.append(["Amara", "A+"])
    buffer = io.BytesIO()
    wb.save(buffer)
    excel_bytes = buffer.getvalue()

    result = parse_uploaded_file("grades.xlsx", excel_bytes)
    assert result.file_type == "excel"
    assert "Amara" in result.extracted_text
