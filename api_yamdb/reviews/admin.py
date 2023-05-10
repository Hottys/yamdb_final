from django.contrib import admin

from reviews.models import Category, Comment, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year', 'description')
    search_fields = ('name', 'year')
    list_filter = ('category',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'score')
    search_fields = ('title',)
    list_filter = ('score',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text')
    search_fields = ('review',)
