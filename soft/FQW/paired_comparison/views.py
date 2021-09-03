from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from pandas import DataFrame

from .forms import ComparisonsForm, UsersForm
from .fun import read_file, create_comparison, get_comparison_user, set_result, get_targets_to_dict, create_user
from .models import Comparisons, Users, ComparisonUser


def index(request: WSGIRequest) -> HttpResponse:
    return render(request, 'main/index.html')


def load(request: WSGIRequest) -> HttpResponse:
    data: dict = {}
    if request.method == 'POST':
        form: ComparisonsForm
        form = ComparisonsForm(request.POST, request.FILES, )
        if form.is_valid():
            raw_file: InMemoryUploadedFile = None
            file: DataFrame = None
            data['errors'] = []
            try:
                raw_file, file = read_file(request)
            except (ValueError, IOError):
                data['errors'].append('Файл не является таблицей excel')
            if raw_file and not file.empty:
                comparison: Comparisons = create_comparison(request.POST, raw_file, file)
                return redirect('compare_admin', id=comparison.id, admin_token=comparison.url)
            try:
                if file.empty:
                    data['errors'].append('Список не распознан. Возможно файл был пустым?')
            except AttributeError:
                if not ('Файл не является таблицей excel' in data['errors']):
                    data['errors'].append('Файл не является таблицей excel')
    else:
        form = ComparisonsForm()
    data['form'] = form
    return render(request, 'main/load.html', data)


def compare_target(request: WSGIRequest, id: int) -> HttpResponse:
    data: dict = {}
    response: HttpResponse = None
    try:
        comparison: Comparisons = Comparisons.objects.get(id=id)
    except Comparisons.DoesNotExist:
        data['errors'] = ['Список для попарного сравнения не найден. Проверьте правильность введенной ссылки.']
        response = render(request, 'main/compare.html', data)
    else:
        try:
            user_id: str = request.COOKIES['uuid']
        except KeyError:
            return redirect('new_user', id=id)
        else:
            data['comparison'] = comparison
            response = render(request, 'main/compare.html', data)
            response.set_cookie('uuid', user_id, max_age=60 * 60 * 24 * 31)
    return response


def compare_admin(request: WSGIRequest, id: int, admin_token: str) -> HttpResponse:
    data: dict = {}
    try:
        comparison: Comparisons = Comparisons.objects.get(id=id, url=admin_token)
    except Comparisons.DoesNotExist:
        data['errors'] = ['Доступ запрещен. Проверьте правильность введенной ссылки.']
    else:
        data['comparison'] = comparison
        data['objects'] = comparison.objects_set.order_by('raw_id').all()
        data['results'] = comparison.comparisonuser_set.all()
        data['users'] = comparison.users.all()
        host: str = request.META["HTTP_HOST"]
        data['urls'] = {
            'main': f'{host}{reverse(compare_target, args=[comparison.id])}',
            'admin': f'{host}{reverse(compare_admin, args=[comparison.id, comparison.url])}'
        }
    return render(request, 'main/compare_admin.html', data)


def get_targets(request: WSGIRequest, id: int) -> JsonResponse:
    data: dict = {}
    comparison: Comparisons = Comparisons.objects.get(id=id)
    data['comparison'] = {
        'id': comparison.id,
        'title': comparison.title,
        'description': comparison.description,
        'parameters_title': comparison.parameters_title
    }
    try:
        user: Users = Users.objects.get(uuid=request.COOKIES['uuid'])
    except Users.DoesNotExist:
        data = {'new_user': True}
    else:
        comparison_user: ComparisonUser = get_comparison_user(comparison, user)
        if request.body != b'':
            set_result(request.body, comparison_user)
        data.update(get_targets_to_dict(comparison, comparison_user))
    return JsonResponse(data)


def new_user(request: WSGIRequest, id: int) -> HttpResponse:
    response: HttpResponse
    if request.method == 'POST':
        user: Users = create_user(request.POST)
        response = redirect('compare_target', id=id)
        response.set_cookie('uuid', user.uuid, max_age=60 * 60 * 24 * 31)
    else:
        form: UsersForm = UsersForm()
        data: dict = {
            'form': form,
        }
        response = render(request, 'main/create_user.html', data)
    return response