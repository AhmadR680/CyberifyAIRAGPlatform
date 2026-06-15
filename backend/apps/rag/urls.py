from django.urls import path
from .views import RAGSearchView

urlpatterns = [
    path("search/", RAGSearchView.as_view(), name="rag-search"),
]
