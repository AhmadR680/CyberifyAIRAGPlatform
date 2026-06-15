from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import search_documents

class RAGSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query", "")
        if not query:
            return Response({"results": []})
        
        results = search_documents(request.user.workspace, query)
        return Response({"results": results})
