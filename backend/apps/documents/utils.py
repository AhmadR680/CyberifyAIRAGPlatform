import fitz  # PyMuPDF
import docx


def extract_text(
    file_path
):
    if file_path.endswith(
        ".pdf"
    ):
        return extract_pdf_text(
            file_path
        )

    elif file_path.endswith(
        ".docx"
    ):
        return extract_docx_text(
            file_path
        )

    elif file_path.endswith(
        ".txt"
    ):
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    return ""


def extract_pdf_text(
    file_path
):
    text = ""

    pdf = fitz.open(
        file_path
    )

    for page in pdf:
        text += page.get_text()

    return text


def extract_docx_text(
    file_path
):
    doc = docx.Document(
        file_path
    )

    return "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
    )