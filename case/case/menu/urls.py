from django.urls import path
from .views import menu_example_view, about_view, team_view

urlpatterns = [
    path('menu-example/', menu_example_view, name='menu_example'),
    path('about/', about_view, name='about'),
    path('about/team/', team_view, name='team'),
]
