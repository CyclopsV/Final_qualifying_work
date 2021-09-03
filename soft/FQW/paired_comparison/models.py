from datetime import datetime
from uuid import uuid4, UUID

from django.contrib.postgres.fields import ArrayField
from django.db.models import Model, CharField, TextField, FileField, DateTimeField, ForeignKey, CASCADE, UUIDField, \
    IntegerField, SET_NULL, ManyToManyField, EmailField
from django.db.models.fields.files import FieldFile

from .setting_models import create_url


class Users(Model):
    uuid: UUID = UUIDField(primary_key=True, default=uuid4)
    name: str = CharField('Имя', max_length=200)
    email: str = EmailField(max_length=250, blank=True)
    first_visit: datetime = DateTimeField(auto_now=True)

    def __str__(self):
        return f'User: {self.name} ({self.uuid})'


class Comparisons(Model):
    title: str = CharField('Название', max_length=200)
    description: str = TextField('Описание', blank=True)
    parameters_title: list = ArrayField(TextField('Название параметров'), null=True)
    url: str = CharField('Адрес для просмотра результатов', max_length=50, default=create_url)
    upload_date: datetime = DateTimeField(auto_now=True)
    file: FieldFile = FileField('Файл', upload_to='upload_file')
    result_fin: list = ArrayField(ArrayField(IntegerField()), null=True)
    users = ManyToManyField(Users, through='ComparisonUser')

    def __str__(self):
        return f'Comparison: {self.id}. {self.title}'


class Objects(Model):
    raw_id: int = IntegerField()
    title: str = TextField('Название объекта')
    parameters: list = ArrayField(TextField('Параметр'))
    number_comparisons: int = IntegerField(default=0)
    comparison: Comparisons = ForeignKey(Comparisons, on_delete=CASCADE)

    def __str__(self):
        return f'{self.raw_id}. {self.title} -> {self.comparison}'


class ComparisonUser(Model):
    user: Users = ForeignKey(Users, null=True, on_delete=SET_NULL)
    comparison: Comparisons = ForeignKey(Comparisons, on_delete=CASCADE)
    start: datetime = DateTimeField(auto_now=True)
    final: datetime = DateTimeField(null=True)
    result: list = ArrayField(ArrayField(IntegerField()), null=True)

    def __str__(self):
        return f'{self.comparison} -> {self.user}'
