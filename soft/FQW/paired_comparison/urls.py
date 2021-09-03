from django.urls import path

from .views import load, index, compare_admin, compare_target, get_targets, new_user

urlpatterns = (
    path('', index, name='home'),
    path('load', load, name='load'),
    # path('compare', compare, name='compare'),
    path('compare/<int:id>', compare_target, name='compare_target'),
    path('compare/<int:id>/get_targets', get_targets, name='get_targets'),
    path('compare/<int:id>/create_user', new_user, name='new_user'),
    path('compare/<int:id>/<str:admin_token>', compare_admin, name='compare_admin'),
)
