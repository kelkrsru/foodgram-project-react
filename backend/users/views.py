from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from users.paginators import PageLimitPagination
from users.serializers import (PasswordSerializer, UserSerializer,
                               UserSubscribeSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for model User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageLimitPagination

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        else:
            return super().get_object()

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод "DELETE" не разрешен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(data=request.data,
                                        context={'request': request})
        if serializer.is_valid():
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=UserSubscribeSerializer)
    def subscribe(self, request, pk):
        user = request.user
        author_id = int(pk)
        author = get_object_or_404(User, pk=author_id)
        if request.method == 'POST':
            if author_id == request.user.id:
                return Response(
                    {'errors': 'Невозможно подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if User.objects.filter(subscribe=author_id).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscribe.add(author)
            serializer = self.get_serializer(author, context={
                'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if User.objects.filter(subscribe=author_id).exists():
                user.subscribe.remove(author)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Вы не подписаны на этого автора.'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
