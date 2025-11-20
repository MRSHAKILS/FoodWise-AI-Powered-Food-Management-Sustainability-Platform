from django.shortcuts import render


def upload_form(request):
    return render(request, 'uploads/upload_form.html')
