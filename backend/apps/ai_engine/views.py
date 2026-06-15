from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ContractAnalysis, ComplianceScore, ChatHistory
from .serializers import ContractAnalysisSerializer, ComplianceScoreSerializer, ChatHistorySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.documents.models import Document
from apps.rag.services import generate_embedding
from apps.rag.models import DocumentChunk
from django.db import models
from pgvector.django import CosineDistance
from groq import Groq
from django.conf import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY)

class ContractAnalysisListView(generics.ListAPIView):
    serializer_class = ContractAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ContractAnalysis.objects.filter(document__workspace=self.request.user.workspace)

class ComplianceScoreListView(generics.ListAPIView):
    serializer_class = ComplianceScoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ComplianceScore.objects.filter(document__workspace=self.request.user.workspace)

class DocumentChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, workspace=request.user.workspace)
        history = ChatHistory.objects.filter(document=document, user=request.user)
        serializer = ChatHistorySerializer(history, many=True)
        return Response(serializer.data)

    def post(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, workspace=request.user.workspace)
        message = request.data.get("message")
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve Context via RAG
        provider = document.workspace.llm_provider
        query_embedding = generate_embedding(message, provider=provider)
        chunks = DocumentChunk.objects.filter(document=document).order_by(
            CosineDistance('embedding', query_embedding)
        )[:5]
        context_text = "\n\n".join([c.text for c in chunks])

        # Retrieve last 5 chat history for context
        history = ChatHistory.objects.filter(document=document, user=request.user).order_by("-created_at")[:5]
        messages = [{"role": "system", "content": "You are a helpful AI assistant. Answer the user's questions based on the provided document context. If the answer is not in the context, say you don't know based on the document."}]
        
        for h in reversed(history):
            messages.append({"role": "user", "content": h.user_message})
            messages.append({"role": "assistant", "content": h.ai_response})

        messages.append({"role": "user", "content": f"Context from document:\n{context_text}\n\nQuestion: {message}"})

        ai_response = ""

        try:
            if provider == "openai":
                from openai import OpenAI
                openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.3
                )
                ai_response = response.choices[0].message.content.strip()
            elif provider == "gemini":
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                # Convert messages format to text
                gemini_prompt = ""
                for m in messages:
                    gemini_prompt += f"{m['role'].capitalize()}: {m['content']}\n\n"
                    
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=gemini_prompt,
                )
                ai_response = response.text.strip()
            else:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.3
                )
                ai_response = response.choices[0].message.content.strip()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        chat_history = ChatHistory.objects.create(
            document=document,
            user=request.user,
            user_message=message,
            ai_response=ai_response
        )

        return Response(ChatHistorySerializer(chat_history).data, status=status.HTTP_201_CREATED)
