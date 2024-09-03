from django.shortcuts import render


def menu_example_view(request):
    return render(request, 'menu/menu_example.html')


def about_view(request):
    return render(request, 'menu/about.html')


def team_view(request):
    return render(request, 'menu/team.html')