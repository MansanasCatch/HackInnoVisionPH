"""Document and file ingestion parser supporting Image, PDF, Word, Excel, CSV, and Text files."""

import base64
import io
import os

import openpyxl
from docx import Document  # type: ignore
from pypdf import PdfReader  # type: ignore

from app.core.logging import get_logger
from app.schemas.ai import ExtractedFileContent

logger = get_logger(__name__)


def parse_uploaded_file(
    filename: str, content_bytes: bytes, content_type: str | None = None
) -> ExtractedFileContent:
    """Extract clean text content and metadata from uploaded file bytes."""
    ext = os.path.splitext(filename)[1].lower().strip(".")
    ct = (content_type or "").lower()

    # Determine broad file category
    if ext in ["jpg", "jpeg", "png", "webp", "bmp", "gif"] or "image/" in ct:
        return _parse_image(filename, content_bytes, ct or f"image/{ext}")
    elif ext == "pdf" or "pdf" in ct:
        return _parse_pdf(filename, content_bytes)
    elif ext in ["docx", "doc"] or "word" in ct:
        return _parse_word(filename, content_bytes)
    elif ext in ["xlsx", "xls"] or "spreadsheet" in ct or "excel" in ct:
        return _parse_excel(filename, content_bytes)
    elif ext == "csv" or "csv" in ct:
        return _parse_csv(filename, content_bytes)
    else:
        return _parse_text(filename, content_bytes, ext or "txt")


def _parse_image(filename: str, content_bytes: bytes, content_type: str) -> ExtractedFileContent:
    """Parse image into base64 data payload and descriptive text."""
    b64 = base64.b64encode(content_bytes).decode("utf-8")
    desc = (
        f"[Image File Attached: {filename} ({len(content_bytes)} bytes)]\n"
        "(Base64 data ready for multimodal vision inference)"
    )

    return ExtractedFileContent(
        filename=filename,
        file_type="image",
        content_type=content_type,
        character_count=len(desc),
        extracted_text=desc,
        base64_data=b64,
    )


def _parse_pdf(filename: str, content_bytes: bytes) -> ExtractedFileContent:
    """Extract text from PDF pages."""
    text_parts: list[str] = []
    try:
        reader = PdfReader(io.BytesIO(content_bytes))
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(f"--- Page {idx + 1} ---\n{page_text.strip()}")
    except Exception as err:
        logger.warning("Error reading PDF '%s': %s", filename, err)
        text_parts.append(f"[Error extracting PDF text: {err}]")

    extracted = "\n\n".join(text_parts) if text_parts else "[Empty PDF document]"
    return ExtractedFileContent(
        filename=filename,
        file_type="pdf",
        content_type="application/pdf",
        character_count=len(extracted),
        extracted_text=extracted,
    )


def _parse_word(filename: str, content_bytes: bytes) -> ExtractedFileContent:
    """Extract text paragraphs and tables from Word (.docx) documents."""
    text_parts: list[str] = []
    try:
        doc = Document(io.BytesIO(content_bytes))
        for p in doc.paragraphs:
            if p.text.strip():
                text_parts.append(p.text.strip())

        # Extract table contents
        for t_idx, table in enumerate(doc.tables):
            table_lines = [f"\n[Table {t_idx + 1}]"]
            for row in table.rows:
                row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                table_lines.append(" | ".join(row_cells))
            text_parts.append("\n".join(table_lines))
    except Exception as err:
        logger.warning("Error reading Word document '%s': %s", filename, err)
        text_parts.append(f"[Error extracting Word content: {err}]")

    extracted = "\n".join(text_parts) if text_parts else "[Empty Word document]"
    return ExtractedFileContent(
        filename=filename,
        file_type="word",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        character_count=len(extracted),
        extracted_text=extracted,
    )


def _parse_excel(filename: str, content_bytes: bytes) -> ExtractedFileContent:
    """Extract worksheet contents from Excel (.xlsx) files into markdown tables."""
    text_parts: list[str] = []
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content_bytes), data_only=True)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                continue

            text_parts.append(f"\n--- Sheet: {sheet_name} ---")
            for r in rows:
                # filter trailing empty cells
                filtered = [str(c) if c is not None else "" for c in r]
                if any(filtered):
                    text_parts.append(" | ".join(filtered))
    except Exception as err:
        logger.warning("Error reading Excel file '%s': %s", filename, err)
        text_parts.append(f"[Error extracting Excel content: {err}]")

    extracted = "\n".join(text_parts) if text_parts else "[Empty Excel workbook]"
    return ExtractedFileContent(
        filename=filename,
        file_type="excel",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        character_count=len(extracted),
        extracted_text=extracted,
    )


def _parse_csv(filename: str, content_bytes: bytes) -> ExtractedFileContent:
    """Extract CSV file content."""
    try:
        decoded = content_bytes.decode("utf-8", errors="replace")
    except Exception:
        decoded = content_bytes.decode("latin-1", errors="replace")

    return ExtractedFileContent(
        filename=filename,
        file_type="csv",
        content_type="text/csv",
        character_count=len(decoded),
        extracted_text=decoded,
    )


def _parse_text(filename: str, content_bytes: bytes, ext: str) -> ExtractedFileContent:
    """Extract plain text, markdown, or code files."""
    try:
        decoded = content_bytes.decode("utf-8", errors="replace")
    except Exception:
        decoded = content_bytes.decode("latin-1", errors="replace")

    return ExtractedFileContent(
        filename=filename,
        file_type=ext if ext else "text",
        content_type="text/plain",
        character_count=len(decoded),
        extracted_text=decoded,
    )
