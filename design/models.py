from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _('Пользователь с таким именем уже существует.')
        },
    )
    first_name = models.CharField(_('Имя'), max_length=150, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=150, blank=True)
    email = models.EmailField(_('Email'), unique=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=150, help_text="Название категории", verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Application(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    title = models.CharField(max_length=150, verbose_name="Название заявки")
    description = models.TextField(max_length=500, verbose_name="Описание заявки")
    image = models.FileField(upload_to='applications/', verbose_name="Загрузите фото заявки")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория заявки')
    design_image = models.FileField(upload_to='designs/', verbose_name="Фото готового дизайна", blank=True, null=True)

    STATUS_CHOICES = [
        ('N', "Новая"),
        ('P', "Принято в работу"),
        ('D', 'Выполнено')
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="N", verbose_name='Статус заявки')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заявки")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий к заявке")
    favorite = models.BooleanField(default=False, verbose_name='Добавить в избранное')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-date']

    def __str__(self):
        return self.title