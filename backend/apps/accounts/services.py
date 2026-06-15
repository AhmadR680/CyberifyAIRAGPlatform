class WorkspaceFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter(
            workspace=self.request.user.workspace
        )