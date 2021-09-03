from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet
from django.forms import model_to_dict
from django.http import QueryDict
from django.utils.datastructures import MultiValueDictKeyError
from pandas import DataFrame, read_excel

from .models import Objects, Comparisons, Users, ComparisonUser


def get_file(raw_file: InMemoryUploadedFile, check_index: bool = False) -> tuple:
    raw_file: InMemoryUploadedFile = raw_file
    file_name: list = raw_file.name.split('.')
    raw_file.name = datetime.now().strftime('%Y.%m.%d_%H.%M.%S.%f.') + file_name[-1]
    file: DataFrame
    if check_index:
        file = read_excel(raw_file, index_col=0)
    else:
        file = read_excel(raw_file)
    return raw_file, file


def read_file(request) -> tuple:
    try:
        if request.POST['index_check']:
            raw_file, file = get_file(request.FILES['file'], True)
    except MultiValueDictKeyError:
        raw_file, file = get_file(request.FILES['file'])
    return raw_file, file


def create_comparison(info: QueryDict, raw_file: InMemoryUploadedFile, file: DataFrame) -> Comparisons:
    comparison: Comparisons = Comparisons()
    comparison.title = info['title']
    comparison.description = info['description']
    comparison.file = raw_file
    comparison.parameters_title = list(file.columns)[1:]
    comparison.save()

    create_objects(file, comparison)
    comparison.result_fin = create_matrix(comparison.objects_set.count())
    comparison.save()
    return comparison


def create_objects(file: DataFrame, comparison: Comparisons):
    zero_index: bool = False
    for i, row in file.iterrows():
        obj: Objects = Objects()
        if (i == 0) and (not zero_index):
            zero_index = True
        if zero_index:
            obj.raw_id = i
        else:
            obj.raw_id = i - 1
        obj.title = row[0]
        obj.parameters = list(row[1:])
        obj.comparison = comparison
        obj.save()


def create_user(info: QueryDict) -> Users:
    user: Users = Users()
    user.name = info['name']
    user.email = info['email']
    user.save()
    return user


def create_matrix(count: int) -> list:
    result: list = []
    for i in range(count):
        a = []
        for j in range(count):
            if i == j:
                a.append(0)
            else:
                a.append(None)
        result.append(a)
    return result


def get_comparison_user(comparison: Comparisons, user: Users) -> ComparisonUser:
    comparison_user: ComparisonUser
    try:
        comparison_user = ComparisonUser.objects.get(comparison=comparison, user=user)
    except ComparisonUser.DoesNotExist:
        comparison_user = ComparisonUser()
        comparison_user.comparison = comparison
        comparison_user.user = user
        comparison_user.result = create_matrix(comparison.objects_set.count())
        comparison_user.save()
    return comparison_user


def get_targets_to_dict(comparison: Comparisons, comparison_user: ComparisonUser) -> dict:
    data: dict = {}
    targets: QuerySet = comparison.objects_set.order_by('number_comparisons')
    for target in targets:
        target_result: list = comparison_user.result[target.raw_id]
        if None in target_result:
            opponent_index: int = target_result.index(None)
            opponent = comparison.objects_set.get(raw_id=opponent_index)
            data['targets'] = [model_to_dict(target), model_to_dict(opponent)]
            break
    else:
        comparison_user.final = datetime.now()
        comparison_user.save()
        data['errors'] = ['Вы оценили все возможные варианты']
    return data


def set_result(request: bytes, comparison_user: ComparisonUser):
    players: dict = eval(request)
    result: list
    if players.get('draw'):
        result = [0, 0]
    else:
        result = [1, -1]
    winner: Objects = Objects.objects.get(id=players['winner'])
    loser: Objects = Objects.objects.get(id=players['loser'])
    winner.number_comparisons += 1
    loser.number_comparisons += 1
    comparison_user.result[winner.raw_id][loser.raw_id] = result[0]
    comparison_user.result[loser.raw_id][winner.raw_id] = result[1]
    comparison: Comparisons = comparison_user.comparison
    if comparison.result_fin[winner.raw_id][loser.raw_id] is None:
        comparison.result_fin[winner.raw_id][loser.raw_id] = 0
    if comparison.result_fin[loser.raw_id][winner.raw_id] is None:
        comparison.result_fin[loser.raw_id][winner.raw_id] = 0
    comparison.result_fin[winner.raw_id][loser.raw_id] += result[0]
    comparison.result_fin[loser.raw_id][winner.raw_id] += result[1]

    winner.save()
    loser.save()
    comparison_user.save()
    comparison.save()
