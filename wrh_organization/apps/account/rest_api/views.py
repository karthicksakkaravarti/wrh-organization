from django.contrib.auth import authenticate, login, logout

from rest_framework import viewsets, permissions, status

from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from .serializers import SessionSerializer, UserProfileSerializer, SetPasswordSerializer, UserSessionSerializer, \
    SetPrefsSerializer


class SessionView(viewsets.ViewSet):
    class SessionPermission(permissions.BasePermission):
        """ custom class to check permissions for sessions """

        def has_permission(self, request, view):
            """ check request permissions """
            if request.method == 'POST':
                return True
            return request.user.is_authenticated and request.user.is_active

    permission_classes = (SessionPermission,)
    serializer_class = SessionSerializer

    def get(self, request, *args, **kwargs):
        """ api to get current session """
        return Response(UserSessionSerializer(request.user, context={'request': request}).data)

    def post(self, request, *args, **kwargs):
        """ api to login """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.data)
        if not user:
            return Response({'detail': 'Username or password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({'detail': 'User is inactive'}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response(UserSessionSerializer(user, context={'request': request}).data)

    def delete(self, request, *args, **kwargs):
        """ api to logout """

        user_id = request.user.id
        logout(request)
        return Response({'id': user_id})

    create = post  # this is a trick to show this view in api-root


class ProfileView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    parser_classes = list(viewsets.ViewSet.parser_classes) + [FileUploadParser]

    def list(self, request, *args, **kwargs):
        return Response(self.serializer_class(request.user, context={'request': request}).data)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, data=request.data, partial=True,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['PUT'])
    def password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.validated_data['new_password'])
        self.request.user.save(update_fields=['password'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET', 'PUT'], serializer_class=SetPrefsSerializer)
    def prefs(self, request, *args, **kwargs):
        if request.method == 'PUT':
            serializer = SetPrefsSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            prefs = self.request.user.prefs or {}
            prefs.update(serializer.validated_data)
            self.request.user.prefs = prefs
            self.request.user.save(update_fields=['prefs'])

        return Response(self.request.user.prefs)

    create = put
