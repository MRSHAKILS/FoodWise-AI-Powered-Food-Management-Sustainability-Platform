from django.shortcuts import render


def resources_list(request):
    return render(request, 'resources/resources_list.html')
