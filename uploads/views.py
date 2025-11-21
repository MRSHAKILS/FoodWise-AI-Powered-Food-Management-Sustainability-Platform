from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Upload
from .forms import UploadForm
from food.models import FoodItem, ConsumptionLog
from .ocr_utils import process_upload_with_ocr


@login_required
def upload_form(request):
    """Handle image upload for receipts, food labels, etc."""
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            
            # Auto-set file metadata
            if upload.file:
                upload.file_name = upload.file.name
                upload.file_size = upload.file.size
                
                # Set MIME type
                file_extension = upload.file.name.split('.')[-1].lower()
                mime_types = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                }
                upload.mime_type = mime_types.get(file_extension, 'application/octet-stream')
            
            upload.save()
            
            # Always process images with AI automatically
            if upload.mime_type and upload.mime_type.startswith('image/'):
                messages.info(request, f'🔄 Processing image with AI...')
                
                try:
                    result = process_upload_with_ocr(upload)
                    
                    if result['success']:
                        messages.success(
                            request,
                            f'✅ {result["message"]}! Added {result["created_count"]} items to your inventory.'
                        )
                        # Redirect to inventory instead of upload list
                        return redirect('food:inventory_list')
                    else:
                        messages.warning(
                            request,
                            f'⚠️ {result["message"]}'
                        )
                        if result.get('errors'):
                            for error in result['errors']:
                                messages.error(request, error)
                        return redirect('uploads:upload_detail', pk=upload.pk)
                except Exception as e:
                    error_msg = str(e)
                    if 'quota' in error_msg.lower() or 'limit' in error_msg.lower() or '429' in error_msg:
                        messages.error(
                            request,
                            f'⚠️ API Quota Exceeded: Your Gemini API free tier limit may have been reached. '
                            f'Check your usage at https://makersuite.google.com/'
                        )
                    elif 'GEMINI_API_KEY' in error_msg:
                        messages.error(request, f'🔑 API Key Error: {error_msg}')
                    else:
                        messages.error(request, f'❌ AI processing failed: {error_msg}')
                    
                    return redirect('uploads:upload_detail', pk=upload.pk)
            else:
                messages.success(
                    request,
                    f'✅ File "{upload.file_name}" uploaded successfully! '
                    f'({upload.get_file_size_display()})'
                )
                return redirect('uploads:upload_list')
        else:
            messages.error(request, '❌ Upload failed. Please check the errors below.')
    else:
        form = UploadForm()
    
    context = {
        'form': form,
    }
    return render(request, 'uploads/upload_form.html', context)


@login_required
def upload_list(request):
    """Display all uploaded images for current user with filtering"""
    uploads = Upload.objects.filter(user=request.user)
    
    # Filter by file type if provided
    file_type = request.GET.get('file_type')
    if file_type and file_type != 'all':
        uploads = uploads.filter(file_type=file_type)
    
    # Get filter options
    file_types = Upload.FILE_TYPE_CHOICES
    
    # Statistics
    total_uploads = uploads.count()
    total_size = sum(upload.file_size for upload in uploads)
    total_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
    
    context = {
        'uploads': uploads,
        'file_types': file_types,
        'selected_type': file_type or 'all',
        'total_uploads': total_uploads,
        'total_size_mb': total_size_mb,
    }
    return render(request, 'uploads/uploads_list.html', context)


@login_required
def upload_detail(request, pk):
    """Show single upload with metadata and association options"""
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    # Get user's inventory items and logs for potential association
    inventory_items = FoodItem.objects.filter(user=request.user).order_by('-created_at')
    consumption_logs = ConsumptionLog.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    context = {
        'upload': upload,
        'inventory_items': inventory_items,
        'consumption_logs': consumption_logs,
        'can_process_ocr': upload.mime_type and upload.mime_type.startswith('image/'),
    }
    return render(request, 'uploads/upload_detail.html', context)


@login_required
def process_ocr_view(request, pk):
    """Manually trigger OCR processing for an uploaded image"""
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    # Check if it's an image
    if not upload.mime_type or not upload.mime_type.startswith('image/'):
        messages.error(request, '❌ Only image files can be processed with OCR.')
        return redirect('uploads:upload_detail', pk=pk)
    
    # Check if already processed
    if upload.processed:
        messages.info(request, 'ℹ️ This image has already been processed.')
        return redirect('uploads:upload_detail', pk=pk)
    
    messages.info(request, f'🔄 Processing "{upload.file_name}" with AI...')
    
    try:
        result = process_upload_with_ocr(upload)
        
        if result['success']:
            messages.success(
                request,
                f'✅ {result["message"]}! Added {result["created_count"]} items to your inventory.'
            )
        else:
            messages.warning(
                request,
                f'⚠️ {result["message"]}'
            )
            if result.get('errors'):
                for error in result['errors']:
                    messages.error(request, error)
    except Exception as e:
        error_msg = str(e)
        # Check for quota/limit errors
        if 'quota' in error_msg.lower() or 'limit' in error_msg.lower() or '429' in error_msg:
            messages.error(
                request,
                f'⚠️ API Quota Exceeded: Your Gemini API free tier limit may have been reached. '
                f'Check your usage at https://makersuite.google.com/ or wait a few minutes and try again.'
            )
        elif 'GEMINI_API_KEY' in error_msg:
            messages.error(
                request,
                f'🔑 API Key Error: {error_msg}'
            )
        else:
            messages.error(
                request,
                f'❌ AI processing failed: {error_msg}'
            )
    
    return redirect('uploads:upload_detail', pk=pk)


@login_required
def upload_delete(request, pk):
    """Delete uploaded file and database record"""
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    # Store filename for message
    filename = upload.file_name
    
    # Delete the file from filesystem and database
    upload.file.delete(save=False)
    upload.delete()
    
    messages.success(request, f'🗑️ Upload "{filename}" deleted successfully.')
    return redirect('uploads:upload_list')


@login_required
def link_to_inventory(request, pk):
    """Link uploaded image to inventory item or consumption log"""
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    if request.method == 'POST':
        link_type = request.POST.get('link_type')
        item_id = request.POST.get('item_id')
        
        if link_type == 'inventory' and item_id:
            try:
                item = FoodItem.objects.get(pk=item_id, user=request.user)
                upload.associated_inventory = item
                upload.associated_log = None  # Clear log association
                upload.save()
                messages.success(
                    request,
                    f'🔗 Image linked to inventory item: {item.name}'
                )
            except FoodItem.DoesNotExist:
                messages.error(request, '❌ Inventory item not found.')
        
        elif link_type == 'log' and item_id:
            try:
                log = ConsumptionLog.objects.get(pk=item_id, user=request.user)
                upload.associated_log = log
                upload.associated_inventory = None  # Clear inventory association
                upload.save()
                messages.success(
                    request,
                    f'🔗 Image linked to consumption log: {log.item_name}'
                )
            except ConsumptionLog.DoesNotExist:
                messages.error(request, '❌ Consumption log not found.')
        
        elif link_type == 'unlink':
            upload.associated_inventory = None
            upload.associated_log = None
            upload.save()
            messages.success(request, '🔓 Image unlinked from all items.')
        
        else:
            messages.error(request, '❌ Invalid link request.')
        
        return redirect('uploads:upload_detail', pk=pk)
    
    # GET request - show link form
    inventory_items = FoodItem.objects.filter(user=request.user).order_by('-created_at')
    consumption_logs = ConsumptionLog.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    context = {
        'upload': upload,
        'inventory_items': inventory_items,
        'consumption_logs': consumption_logs,
    }
    return render(request, 'uploads/link_to_inventory.html', context)


@login_required
@require_POST
def upload_associate_api(request, pk):
    """JSON API endpoint to associate upload with inventory or log"""
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    item_type = request.POST.get('item_type')  # 'inventory' or 'log'
    item_id = request.POST.get('item_id')
    
    try:
        if item_type == 'inventory':
            item = FoodItem.objects.get(pk=item_id, user=request.user)
            upload.associated_inventory = item
            upload.associated_log = None
            upload.save()
            return JsonResponse({
                'success': True,
                'message': f'Linked to inventory: {item.name}',
                'item': {
                    'type': 'inventory',
                    'id': item.id,
                    'name': item.name,
                }
            })
        
        elif item_type == 'log':
            log = ConsumptionLog.objects.get(pk=item_id, user=request.user)
            upload.associated_log = log
            upload.associated_inventory = None
            upload.save()
            return JsonResponse({
                'success': True,
                'message': f'Linked to log: {log.item_name}',
                'item': {
                    'type': 'log',
                    'id': log.id,
                    'name': log.item_name,
                }
            })
        
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid item type'
            }, status=400)
    
    except (FoodItem.DoesNotExist, ConsumptionLog.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Item not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
