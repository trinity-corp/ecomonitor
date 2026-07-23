from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Device, SensorReading, DeviceCommand
import csv, json

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'devices/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show devices owned by the current user
        devices = Device.objects.filter(owner=self.request.user)
        context['devices'] = devices
        context['total_readings'] = SensorReading.objects.filter(
            device__owner=self.request.user
        ).count()
        context['active_alerts'] = sum(1 for d in devices if d.is_online)
        return context

class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'devices/device_list.html'
    context_object_name = 'devices'
    def get_queryset(self):
        # Only show devices owned by the current user
        return Device.objects.filter(owner=self.request.user)

class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = Device
    template_name = 'devices/device_detail.html'
    context_object_name = 'device'
    slug_field = 'device_id'
    slug_url_kwarg = 'device_id'
    
    def get_queryset(self):
        # Only allow access to devices owned by the current user
        return Device.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device = self.get_object()
        context['readings'] = device.readings.order_by('-created_at')[:50]
        return context
    
@login_required
def export_readings_csv(request, device_id):
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{device.device_id}_readings.csv"'

    writer = csv.writer(response)
    writer.writerow(['timestamp', 'final_value'])

    for device in SensorReading.objects.filter(device=device).order_by('-id'):
        writer.writerow([device.created_at, device.final_value])
    
    return response

@login_required
def export_readings_json(request, device_id):
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)

    readings = SensorReading.objects.filter(device=device).order_by('-id')
    
    data = []
    for r in readings:
        data.append({
            'created_at': r.created_at.isoformat(),
            'final_value': r.final_value,
        })

    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{device.device_id}_readings.json"'
    return response

@login_required
def device_commands(request, device_id):
    """Command interface for a specific device"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    commands = device.commands.order_by('-created_at')[:10]
    
    return render(request, 'devices/device_commands.html', {
        'device': device,
        'commands': commands
    })

@login_required
def send_command(request, device_id):
    """Send a command to a device"""
    if request.method == 'POST':
        device = get_object_or_404(Device, device_id=device_id, owner=request.user)
        command_type = request.POST.get('command_type')
        payload = request.POST.get('payload', '')
        
        if command_type:
            # Create the command
            DeviceCommand.objects.create(
                device=device,
                command_type=command_type,
                payload=payload
            )
            messages.success(request, f'Command "{command_type}" sent to {device.name}')
        else:
            messages.error(request, 'Please select a command type')
        
        return redirect('device-commands', device_id=device_id)
    
    return redirect('device-commands', device_id=device_id)

@login_required
def command_history(request, device_id):
    """View command history for a device"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    commands = device.commands.order_by('-created_at')
    
    return render(request, 'devices/command_history.html', {
        'device': device,
        'commands': commands
    })

@login_required
def readings_history(request, device_id):
    """View all readings for a device"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    readings = device.readings.order_by('-created_at')

    paginator = Paginator(readings, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'devices/readings_history.html', {
        'device': device,
        'readings': readings,
        'page_obj': page_obj
    })

@login_required
def clear_readings(request, device_id):
    device = get_object_or_404(
        Device,
        device_id=device_id,
        owner=request.user
    )

    if request.method == "POST":
        device.readings.all().delete()
        messages.success(
            request,
            f"Readings cleared for {device.name}"
        )

    return redirect(
        "device-detail-web",
        device_id=device.device_id
    )

@login_required
def device_settings(request, device_id):
    """Settings for a device"""
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)

    if request.method == 'POST':
        # Отримуємо всі дані з форми
        name = request.POST.get('device_name')
        device_reading_time = request.POST.get('device_reading_time')
        min_value = request.POST.get('device_min_value')
        max_value = request.POST.get('device_max_value')
        telegram_user_id = request.POST.get('telegram_user_id')
        telegram_bot_token = request.POST.get('telegram_bot_token')

        # Оновлюємо тільки ті поля, які передані
        if name:
            device.name = name

        if device_reading_time:
            try:
                device.reading_time = int(device_reading_time)
                DeviceCommand.objects.create(
                    device=device,
                    command_type='change_reading_time',
                    payload=device_reading_time
            )
            except ValueError:
                messages.error(request, 'Reading time must be a number.')
                return redirect('device-settings', device_id=device_id)

        if min_value:
            device.min_value_limit = min_value

        if max_value:
            device.max_value_limit = max_value

        if telegram_user_id:
            device.telegram_user_id = telegram_user_id

        if telegram_bot_token:
            device.telegram_bot_token = telegram_bot_token

        # Зберігаємо зміни в базу
        device.save()
        messages.success(request, f'Settings for "{device.name}" were updated successfully.')
        return redirect('device-settings', device_id=device_id)

    return render(request, 'devices/device_settings.html', {'device': device})
