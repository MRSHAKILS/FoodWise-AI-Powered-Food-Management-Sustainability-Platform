from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


def upload_form(request):
    # TODO: Implement file upload (JPG/PNG) for food labels/receipts
    # Storage only - NO OCR processing (Phase 6 requirement)
    return render(request, 'uploads/upload_form.html')


def upload_list(request):
    # TODO: Display all uploaded images for current user
    return render(request, 'uploads/upload_list.html')


def upload_detail(request, pk):
    # TODO: Show single upload with metadata
    # upload = get_object_or_404(Upload, pk=pk)
    return render(request, 'uploads/upload_detail.html')


def upload_delete(request, pk):
    # TODO: Delete uploaded file and database record
    # upload = get_object_or_404(Upload, pk=pk)
    # upload.delete()
    return redirect('uploads:upload_list')


def link_to_inventory(request, pk):
    # TODO: Link uploaded image to inventory item or consumption log
    # Manual linking as per Phase 6 requirement
    return render(request, 'uploads/link_to_inventory.html')
