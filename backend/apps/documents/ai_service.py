import json
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def get_json_response(prompt: str, document=None, model="llama-3.3-70b-versatile") -> dict:
    provider = "groq"
    if document and hasattr(document, "workspace") and document.workspace:
        provider = document.workspace.llm_provider

    if provider == "openai":
        from openai import OpenAI
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert AI document analyzer. Always respond with raw valid JSON only. Do not include markdown blocks like ```json."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
    elif provider == "gemini":
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        gemini_prompt = f"You are an expert AI document analyzer. Always respond with raw valid JSON only. Do not include markdown blocks like ```json.\n\nUser request:\n{prompt}"
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=gemini_prompt,
        )
        content = response.text.strip()
    else:
        # Default to Groq
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert AI document analyzer. Always respond with raw valid JSON only. Do not include markdown blocks like ```json."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Failed to decode JSON from AI response:", content)
        return {}

def extract_document_metadata(document, text: str) -> dict:
    prompt = f"""
    Analyze this document and extract the following metadata in JSON format:
    {{
        "document_type": "string",
        "client_name": "string",
        "company_name": "string",
        "important_dates": ["string"],
        "amounts": ["string"],
        "key_clauses": ["string"],
        "summary": "string"
    }}

    Document:
    {text[:10000]}
    """
    return get_json_response(prompt, document=document)

def analyze_contract(document, text: str) -> dict:
    prompt = f"""
    Analyze this contract and provide risks, missing clauses, and recommendations. Return exactly this JSON structure:
    {{
        "summary": "string",
        "risks": ["string"],
        "missing_clauses": ["string"],
        "recommendations": ["string"]
    }}

    Contract:
    {text[:10000]}
    """
    return get_json_response(prompt, document=document)

def check_compliance(document, text: str) -> dict:
    prompt = f"""
    Check this document for compliance issues. Return exactly this JSON structure:
    {{
        "score": integer (0 to 100),
        "issues": ["string"],
        "missing_signatures": boolean,
        "missing_dates": boolean
    }}

    Document:
    {text[:10000]}
    """
    return get_json_response(prompt, document=document)

def generate_workflow(document, text: str) -> list:
    prompt = f"""
    Based on this document, generate a list of workflow tasks that need to be done. Return exactly this JSON structure:
    {{
        "tasks": [
            {{
                "title": "string",
                "description": "string",
                "assignee": "string (suggested role)",
                "deadline": "string (e.g. 'Within 7 days')"
            }}
        ]
    }}

    Document:
    {text[:10000]}
    """
    data = get_json_response(prompt, document=document)
    return data.get("tasks", [])