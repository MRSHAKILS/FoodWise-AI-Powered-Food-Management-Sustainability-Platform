from django.shortcuts import render


def inventory_list(request):
    return render(request, 'food/inventory_list.html')


def inventory_form(request):
    return render(request, 'food/inventory_form.html')
