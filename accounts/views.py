from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from devices.models import Device, DeviceCommand

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import EmailUserCreationForm, EmailAuthenticationForm
from devices.models import Device

@csrf_protect
def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.email}')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@csrf_protect
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.email}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def profile_view(request):
    """User profile view"""
    user_devices = Device.objects.filter(owner=request.user)
    return render(request, 'accounts/profile.html', {
        'devices': user_devices
    })

@login_required
def change_password_view(request):
    """Change password view"""
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def register_device(request):
    """Register a new device to the user's account"""
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        device_name = request.POST.get('device_name', '').strip()
        
        if not device_id:
            messages.error(request, 'Device ID is required')
            return redirect('register-device')
        
        # Check if device already exists
        if Device.objects.filter(device_id=device_id).exists():
            messages.error(request, 'This device is already registered to another account')
            return redirect('register-device')
        
        # Create device linked to current user
        device = Device.objects.create(
            owner = request.user,
            device_id = device_id,
            name = device_name or f'My device {device_id[-6:]}'
        )
        
        messages.success(request, f'Device {device_id} registered successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/register_device.html')

@login_required
def unregister_device(request, device_id):
    """Remove device from user's account"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    
    if request.method == 'POST':
        device_name = device.device_id
        device.delete()
        messages.success(request, f'Device {device_name} removed from your account')
        return redirect('profile')
    
    return render(request, '', {'device': device})

@login_required
def device_management(request):
    """Device management page"""
    user_devices = Device.objects.filter(owner=request.user)
    return render(request, 'accounts/device_management.html', {
        'devices': user_devices
    })

@login_required
def send_device_command(request, device_id):
    """Send a command to a specific device"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    
    if request.method == 'POST':
        command_type = request.POST.get('command_type')
        payload = request.POST.get('payload', '')
        
        if command_type:
            # Create the command
            command = DeviceCommand.objects.create(
                device=device,
                command_type=command_type,
                payload=payload
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Command {command_type} sent to {device.device_id}',
                'command_id': command.id
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def device_commands(request, device_id):
    """View commands for a device"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    commands = device.commands.order_by('-created_at')[:20]
    
    return render(request, 'accounts/device_commands.html', {
        'device': device,
        'commands': commands
    })