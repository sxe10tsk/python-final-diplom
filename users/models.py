from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Переопределяем менеджер пользователя, чтобы email был первым аргументов вместо username
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):

    class UserType(models.TextChoices):
        CUSTOMER = 'customer', 'Заказчик'
        SHOP = 'shop', 'Поставщик'

    username = None #убираем стандартный username из модели AbstractUser
    email = models.EmailField('Email', unique=True)
    user_type = models.CharField(
        'Тип пользователя',
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    is_active = models.BooleanField(default=False)
    company = models.CharField(
        'Название компании поставщика',
        max_length=150,
        null=True,
        blank=True
    )
    USERNAME_FIELD = 'email' #Указываем Django, что email - login
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self):
        return self.email

class Contact(models.Model):

    """
    Контактные данные пользователя, у пользователя может быть много контактов
    у одного контакта только один пользователь
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Заказчик'
    )
    city = models.CharField('Город', max_length=150)
    street = models.CharField('Улица', max_length=150)
    is_private_house = models.BooleanField('Частный дом', default=False)
    house = models.CharField('Дом', max_length=5)
    building = models.CharField('Корпус', max_length=5, blank=True)
    apartment = models.CharField('Квартира', max_length=5, blank=True)
    phone = models.CharField('Номер телефона', max_length=20)
    is_default_adress = models.BooleanField('Адрес по умолчанию', default=False)

    def __str__(self):
        """
        Собираем читаемый адрес
        """
        parts = [self.city, self.street, f'д. {self.house}']
        if self.building:
            parts.append(f'корп. {self.building}')
        if self.apartment:
            parts.append(f'кв. {self.apartment}')
        return ', '.join(parts)
