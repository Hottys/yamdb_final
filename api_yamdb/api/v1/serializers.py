import datetime
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class RegisterDataSerializer(serializers.ModelSerializer):
    # Пробовал не определять поля, но почему-то пайтест не
    # видит параметр длины из модели юзера и начинает ругаться.
    # Возможно тесты код иначе проверяют, ну либо я понять не могу
    email = serializers.EmailField(
        max_length=254
    )
    username = serializers.CharField(
        max_length=150
    )

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate(self, data):
        if data['username'].lower() == 'me':
            raise ValidationError(
                {'Имя пользователя не может быть <me>.'})
        if re.search(
            r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', data['username']
        ) is None:
            raise ValidationError(
                ('Недопустимые символы в username!'),
            )
        user = User.objects.filter(
            username=data.get('username')
        )
        email = User.objects.filter(
            email=data.get('email')
        )
        # Тут что-бы я не пробовал, тесты падают и требуют
        # `email` зарегистрированного пользователя и незанятый `username'
        # должен вернуться ответ со статусом 400.
        if not user.exists() and email.exists():
            raise ValidationError('Недопустимый Email')
        if user.exists() and user.get().email != data.get('email'):
            raise ValidationError('Недопустимый Email')
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        year = datetime.date.today().year
        if not value <= year:
            raise serializers.ValidationError(
                'Нельзя добавить произведение из будущего!'
            )
        return value


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category',)
        model = Title
        read_only = ('id',)

    def validate_year(self, value):
        year = datetime.date.today().year
        if not value <= year:
            raise serializers.ValidationError(
                'Нельзя добавить произведение из будущего!'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only = ('id',)

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user
        if not request.method == 'POST':
            return data
        if title.reviews.filter(author=author).exists():
            raise serializers.ValidationError(
                'Можно оставить только 1 отзыв на произведение!'
            )
        return data

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10!')
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
