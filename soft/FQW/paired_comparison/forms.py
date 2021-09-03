from django.forms import ModelForm, TextInput, Textarea, BooleanField, ClearableFileInput

from .models import Comparisons, Users


class ComparisonsForm(ModelForm):
    index_check = BooleanField(help_text='Является ли первый столбец индексами', required=False, initial='True')

    class Meta:
        model = Comparisons
        fields = ['title', 'description', 'file']
        widgets = {
            'title': TextInput(attrs={
                'placeholder': 'Введите название для попарного сравнения (>200 символов)',
                'class': 'input-field form-elem'
            }),
            'description': Textarea(attrs={
                'placeholder': 'Введите описание для попарного сравнения',
                'class': 'input-field form-elem'
            }),
            'file': ClearableFileInput(attrs={
                'class': 'form-elem'
            })
        }


class UsersForm(ModelForm):
    class Meta:
        model = Users
        fields = ['name', 'email']
        widgets = {
            'name': TextInput(attrs={
                'placeholder': 'ФИО (>200 символов)',
                'class': 'input-field form-elem'
            }),
            'email': TextInput(attrs={
                'placeholder': 'email',
                'class': 'input-field form-elem'
            })
        }
