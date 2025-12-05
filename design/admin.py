from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Application
from django.core.exceptions import ValidationError
from django.db import transaction

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
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
        exclude = ['image']

    design_image = forms.ImageField(required=False,
                                    label='Фото готового дизайна (добавить, если статус меняется на "Выполнено")')
    comment = forms.CharField(required=False,
                              label='Комментарий к работе (добавить, если статус меняется на "Принято на работу")')

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        current_status = self.instance.status if self.instance else None

        if current_status in ['P', 'D'] and status != current_status:
            raise ValidationError("Вы не можете поменять статус заявки, если она имеет статус 'Принято в работу' или 'Выполнено'")

        if status == 'P' and not cleaned_data.get('comment'):
            raise ValidationError('Добавьте комментарий')

        if status == 'D' and not cleaned_data.get('design_image'):
            raise ValidationError('Добавьте фото готового дизайна')

        return cleaned_data

class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = ('user', 'title', 'status', 'category', 'date')
    readonly_fields = ('user', 'title', 'description', 'category', 'date')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'user__username', 'description')
    exclude = ['image']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj:
            status = obj.status

            if status == 'P':
                if 'design_image' in form.base_fields:
                    form.base_fields['design_image'].required = False
                    del form.base_fields['design_image']

            elif status == 'D':
                if 'comment' in form.base_fields:
                    form.base_fields['comment'].required = False
                    del form.base_fields['comment']

        return form

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            obj.commit = form.cleaned_data.get('comment', '')
            obj.design_image = form.cleaned_data.get('design_image', None)
            with transaction.atomic():
                obj.save()


admin.site.register(Category)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Application)