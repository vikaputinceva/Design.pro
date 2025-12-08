from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import CustomUser, Category, Application


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')


        if status == 'P' and not cleaned_data.get('comment'):
            raise ValidationError('Для статуса "Принято в работу" необходим комментарий.')


        if status == 'D' and not cleaned_data.get('design_image'):
            raise ValidationError('Для статуса "Выполнено" необходимо загрузить изображение дизайна.')

        return cleaned_data


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = ['id', 'title', 'get_applicant', 'status', 'category', 'date',
                    'image_preview']
    list_filter = ['status', 'category', 'date']
    search_fields = ['title', 'applicant__username', 'description']
    readonly_fields = ['date', 'image_preview_large', 'get_applicant']
    list_editable = ['status']
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('applicant', 'title', 'description', 'category', 'image')
        }),
        ('Статус и обработка', {
            'fields': ('status', 'comment', 'design_image')
        }),
        ('Дополнительно', {
            'fields': ('date', 'favorite', 'image_preview_large', 'get_applicant'),
            'classes': ('collapse',)
        }),
    )

    def get_applicant(self, obj):
        return obj.applicant.username if obj.applicant else "-"

    get_applicant.short_description = 'Пользователь'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "-"

    image_preview.short_description = 'Изображение'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%;" />',
                obj.image.url
            )
        return "Нет изображения"

    image_preview_large.short_description = 'Предпросмотр изображения'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'application_count']
    search_fields = ['name']
    ordering = ['name']

    def application_count(self, obj):
        return obj.application_set.count()

    application_count.short_description = 'Количество заявок'



admin.site.register(CustomUser, CustomUserAdmin)


admin.site.site_title = 'Design.Pro Администрация'
admin.site.site_header = 'Design.Pro - Панель управления'
admin.site.index_title = 'Управление сайтом'