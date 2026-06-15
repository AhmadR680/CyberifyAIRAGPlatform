from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.workspaces.models import Workspace

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "workspace_name",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def create(self, validated_data):
        workspace_name = validated_data.pop(
            "workspace_name"
        )

        workspace = Workspace.objects.create(
            name=workspace_name,
            slug=workspace_name.lower().replace(" ", "-")
        )

        user = User.objects.create_user(
            **validated_data
        )

        user.workspace = workspace
        user.role = User.Role.OWNER
        user.save()

        return user
    
class UserSerializer(
    serializers.ModelSerializer
):
    workspace = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "workspace",
        ]