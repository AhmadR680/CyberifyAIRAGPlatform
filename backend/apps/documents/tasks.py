from celery import shared_task
from pypdf import PdfReader
from docx import Document as DocxDocument
from .utils import extract_text
from .ai_service import (
    extract_document_metadata,
    analyze_contract,
    check_compliance,
    generate_workflow
)
from .models import Document
import redis
import json
from django.conf import settings

r = redis.Redis.from_url(settings.CELERY_BROKER_URL)

# Safe import to avoid circular dependencies if any
def get_rag_services():
    try:
        from apps.rag.services import process_document_for_rag
        return process_document_for_rag
    except ImportError:
        return None

def get_ai_models():
    from apps.ai_engine.models import ContractAnalysis, ComplianceScore
    from apps.workflows.models import WorkflowTask
    return ContractAnalysis, ComplianceScore, WorkflowTask

def extract_pdf_text(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
            
    # Fallback to OCR if no text found
    if not text.strip():
        try:
            import pytesseract
            from pdf2image import convert_from_path
            pages = convert_from_path(path)
            for page in pages:
                text += pytesseract.image_to_string(page) + "\n"
        except ImportError:
            print("OCR dependencies (pytesseract, pdf2image) not installed. Skipping OCR.")
        except Exception as e:
            print(f"OCR failed: {e}")

    return text

def extract_docx_text(path):
    doc = DocxDocument(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def extract_txt_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()

@shared_task
def process_document(document_id):
    document = Document.objects.get(id=document_id)
    document.status = "processing"
    document.save()

    extracted_text = extract_text(document.file.path)
    document.extracted_text = extracted_text
    
    # 1. Extract Metadata
    metadata = extract_document_metadata(document, extracted_text)
    document.metadata = metadata
    document.save()

    ContractAnalysis, ComplianceScore, WorkflowTask = get_ai_models()

    # 2. RAG Chunking
    process_document_for_rag = get_rag_services()
    if process_document_for_rag:
        process_document_for_rag(document)

    # 3. Contract Analysis (if it's a contract/agreement)
    doc_type = metadata.get("document_type", "").lower()
    if "contract" in doc_type or "agreement" in doc_type:
        contract_data = analyze_contract(document, extracted_text)
        ContractAnalysis.objects.update_or_create(
            document=document,
            defaults={
                "summary": contract_data.get("summary", ""),
                "risks": contract_data.get("risks", []),
                "missing_clauses": contract_data.get("missing_clauses", []),
                "recommendations": contract_data.get("recommendations", [])
            }
        )

    # 4. Compliance Check
    compliance_data = check_compliance(document, extracted_text)
    ComplianceScore.objects.update_or_create(
        document=document,
        defaults={
            "score": compliance_data.get("score", 0),
            "issues": compliance_data.get("issues", []),
            "missing_signatures": compliance_data.get("missing_signatures", False),
            "missing_dates": compliance_data.get("missing_dates", False)
        }
    )

    # 5. Workflow Generation
    WorkflowTask.objects.filter(document=document).delete()
    tasks_data = generate_workflow(document, extracted_text)
    for task in tasks_data:
        WorkflowTask.objects.create(
            document=document,
            title=task.get("title", "New Task"),
            description=task.get("description", ""),
            assignee=task.get("assignee", ""),
            deadline=task.get("deadline", "")
        )

    document.status = "completed"
    document.save()

    # Trigger Notification
    user_id = document.uploaded_by_id if hasattr(document, 'uploaded_by_id') else None
    if user_id:
        message = {
            "type": "processing_complete",
            "document_id": str(document.id),
            "filename": document.filename if hasattr(document, 'filename') else "Document",
            "message": "Document processing completed successfully."
        }
        r.publish(f"user_{user_id}_notifications", json.dumps(message))