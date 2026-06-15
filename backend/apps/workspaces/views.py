from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.documents.models import Document
from apps.workflows.models import WorkflowTask
from apps.ai_engine.models import ComplianceScore, ContractAnalysis

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = request.user.workspace
        
        total_documents = Document.objects.filter(workspace=workspace).count()
        active_workflows = WorkflowTask.objects.filter(document__workspace=workspace).exclude(status='done').count()
        completed_tasks = WorkflowTask.objects.filter(document__workspace=workspace, status='done').count()
        compliance_risks = ComplianceScore.objects.filter(document__workspace=workspace, score__lt=100).count()
        
        recent_docs_qs = Document.objects.filter(workspace=workspace).order_by('-created_at')[:4]
        recent_documents = []
        for doc in recent_docs_qs:
            status_label = "Analyzed" if hasattr(doc, 'contract_analysis') else "Pending"
            recent_documents.append({
                "id": str(doc.id),
                "filename": doc.filename,
                "created_at": doc.created_at.isoformat(),
                "content_type": doc.content_type,
                "status": status_label
            })
            
        action_items = []
        
        missing_sigs = ComplianceScore.objects.filter(document__workspace=workspace, missing_signatures=True)[:3]
        for item in missing_sigs:
            action_items.append({
                "type": "Missing Signatures",
                "description": f"{item.document.filename} is missing required signatures.",
                "severity": "high"
            })
            
        missing_dates = ComplianceScore.objects.filter(document__workspace=workspace, missing_dates=True)[:3]
        for item in missing_dates:
            action_items.append({
                "type": "Missing Dates",
                "description": f"{item.document.filename} is missing execution dates.",
                "severity": "medium"
            })

        return Response({
            "stats": {
                "total_documents": total_documents,
                "active_workflows": active_workflows,
                "compliance_risks": compliance_risks,
                "completed_tasks": completed_tasks
            },
            "recent_documents": recent_documents,
            "action_items": action_items
        })

class WorkspaceSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = request.user.workspace
        users = workspace.users.all()
        
        user_data = []
        for u in users:
            user_data.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active
            })
            
        return Response({
            "workspace": {
                "id": str(workspace.id),
                "name": workspace.name,
                "slug": workspace.slug,
                "created_at": workspace.created_at.isoformat(),
                "is_active": workspace.is_active,
                "llm_provider": workspace.llm_provider
            },
            "users": user_data
        })

    def put(self, request):
        workspace = request.user.workspace
        provider = request.data.get("llm_provider")
        
        if provider in ["groq", "openai", "gemini"]:
            workspace.llm_provider = provider
            workspace.save()
            return Response({"status": "success", "llm_provider": provider})
        return Response({"error": "Invalid provider"}, status=400)
