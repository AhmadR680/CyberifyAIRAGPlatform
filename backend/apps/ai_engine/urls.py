from django.urls import path
from .views import ContractAnalysisListView, ComplianceScoreListView, DocumentChatView

urlpatterns = [
    path("contracts/", ContractAnalysisListView.as_view(), name="contract-analysis-list"),
    path("compliance/", ComplianceScoreListView.as_view(), name="compliance-score-list"),
    path("chat/<uuid:document_id>/", DocumentChatView.as_view(), name="document-chat"),
]
