from django.shortcuts import render
from .dnac_manager import DNAC_Manager

def index(request):
    """Página principal"""
    return render(request, 'dnacenter/index.html')

def authenticate(request):
    """Vista de autenticación"""
    context = {}
    if request.method == 'POST':
        try:
            manager = DNAC_Manager()
            token = manager.get_auth_token()
            context['token'] = token
            context['success'] = True
        except Exception as e:
            context['error'] = str(e)
    return render(request, 'dnacenter/authenticate.html', context)

def list_devices(request):
    """Lista dispositivos de red"""
    context = {}
    try:
        manager = DNAC_Manager()
        devices = manager.get_network_devices()
        context['devices'] = devices
    except Exception as e:
        context['error'] = str(e)
    return render(request, 'dnacenter/devices.html', context)

def device_interfaces(request):
    """Muestra interfaces de un dispositivo"""
    context = {}
    if request.method == 'POST':
        device_ip = request.POST.get('device_ip')
        try:
            manager = DNAC_Manager()
            interfaces = manager.get_device_interfaces(device_ip)
            context['interfaces'] = interfaces
            context['device_ip'] = device_ip
            if not interfaces:
                context['error'] = f'No interfaces found for device {device_ip}'
        except Exception as e:
            context['error'] = str(e)
    return render(request, 'dnacenter/interfaces.html', context)