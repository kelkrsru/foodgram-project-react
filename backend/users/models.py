from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с данным email уже существует.',
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLE_CHOICES,
        default=USER,
        max_length=32,
    )
    subscribe = models.ManyToManyField(
        'self',
        verbose_name='Подписка',
        related_name='subscribers',
        symmetrical=False,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER

    def __str__(self):
        return self.username
