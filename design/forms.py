from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import CustomUser, Application


class CustomUserCreatingForm(forms.ModelForm):
    email = forms.EmailField(label="Адрес электронной почты", max_length=150)

    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-яёЁ\s\-]+$',
                message='Имя должно содержать только кириллические буквы, пробелы и дефисы'
            )
        ]
    )

    last_name = forms.CharField(
        label="Фамилия",
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-яёЁ\s\-]+$',
                message='Фамилия должна содержать только кириллические буквы, пробелы и дефисы'
            )
        ]
    )

    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\-]+$',
                message='Логин должен содержать только латинские буквы и дефисы'
            )
        ]
    )

    agree_to_terms = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True
    )

    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Подтвердить пароль", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Такое имя пользователя занято.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Такой адрес электронной почты занят.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password"))
        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", 'email')


class ApplicationForm(forms.ModelForm):
    title = forms.CharField(label='Название заявки', widget=forms.TextInput)
    description = forms.CharField(label='Описание заявки', widget=forms.Textarea)
    image = forms.FileField(label='Фото заявки', widget=forms.FileInput)

    class Meta:
        model = Application
        fields = ('title', 'description', 'category', 'image')
        widgets = {
            'category': forms.Select
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        max_file_size = 2 * 1024 * 1024

        if image.size > max_file_size:
            raise ValidationError("Размер файла не должен быть больше 2 MB")

        valid_mime_types = ['image/jpeg', 'image/png', 'image/bmp']
        if image.content_type not in valid_mime_types:
            raise ValidationError("Файл должен быть в формате JPG, JPEG, PNG или BMP")

        return image