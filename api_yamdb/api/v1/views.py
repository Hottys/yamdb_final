from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet, NoPutViewSet
from .permissions import AdminOnly, AdminOrReadOnly, IsAuthorOrModerOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, RegisterDataSerializer,
                          ReviewSerializer, TitleCreateSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)

User = get_user_model()


class TitleViewSet(NoPutViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleSerializer
        return TitleCreateSerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = ('slug')


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = ('slug')


class ReviewViewSet(NoPutViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModerOrAdmin,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(NoPutViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerOrAdmin,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


@api_view(['POST'])
def user_register(request):
    serializer = RegisterDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, _ = User.objects.get_or_create(
        **serializer.validated_data
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_EMAIL,
        recipient_list=[user.email],
    )
    return Response(
        serializer.data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
def jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username')
    )
    if default_token_generator.check_token(
        user, serializer.validated_data.get('confirmation_code')
    ):
        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)}, status=status.HTTP_200_OK
        )
    return Response(
        {'confirmation_code': 'Неверный код подтверждения!'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(NoPutViewSet):
    lookup_field = ('username')
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOnly,)
    search_fields = ('username',)
    lookup_field = ('username')

    @action(
        methods=[
            'GET',
            'PATCH',
        ],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def users_own_profile(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'PATCH':
            serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
