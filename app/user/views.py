# Views for user api
from rest_framework import (
    generics,
    authentication,
    status,
    viewsets,
    permissions)
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from core.models import User
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserImageSerializer
    )


class CreateUserView(generics.CreateAPIView):
    # Create a new user in the system
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    # Create a new auth token for user
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    # Manage the authenticated user
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retrieve and return the authenticated user
        return self.request.user


class UserImageView(viewsets.GenericViewSet):
    serializer_class = UserImageSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['POST'],
            detail=True,
            url_path='user-upload-image')
    def upload_image(self, request, pk=None):
        user = User.objects.get(email=self.request.user.email)
        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
