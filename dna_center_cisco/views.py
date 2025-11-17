from django.shortcuts import render
from .api_logic import get_dnac_token, get_device_list, get_device_interfaces
from .models import ApiLog

# View for the authentication page
def get_token_view(request):
    context = {'token': None, 'error': None}
    if request.method == 'POST':
        token = get_dnac_token()
        if token:
            context['token'] = token
            # Store the token in the user's session to use on other pages
            request.session['dnac_token'] = token
        else:
            context['error'] = "Failed to get token. Check logs."

    return render(request, 'dna_center_cisco/get_token.html', context)

# View for listing devices
def device_list_view(request):
    context = {'devices': None, 'error': None}
    token = request.session.get('dnac_token') # Get token from session

    if not token:
        context['error'] = "Authentication required. Please get a token first."
        return render(request, 'dna_center_cisco/device_list.html', context)

    devices, error = get_device_list(token)
    if error:
        context['error'] = error
    else:
        # Filter just the data we want to show
        context['devices'] = [
            {
                'hostname': dev.get('hostname', 'N/A'),
                'type': dev.get('type', 'N/A'),
                'ip': dev.get('managementIpAddress', 'N/A'),
                'serial': dev.get('serialNumber', 'N/A'),
                'software': dev.get('softwareVersion', 'N/A')
            } for dev in devices
        ]

    return render(request, 'dna_center_cisco/device_list.html', context)

# View for listing interfaces of a single device
def interface_list_view(request):
    context = {'interfaces': None, 'error': None, 'device_ip': None}
    token = request.session.get('dnac_token')

    if not token:
        context['error'] = "Authentication required. Please get a token first."
        return render(request, 'dna_center_cisco/interface_list.html', context)

    if request.method == 'POST':
        device_ip = request.POST.get('device_ip')
        context['device_ip'] = device_ip

        if not device_ip:
            context['error'] = "Please provide a device IP."
        else:
            interfaces, error = get_device_interfaces(token, device_ip)
            if error:
                context['error'] = error
            else:
                # Filter the interface data
                context['interfaces'] = [
                    {
                        'name': iface.get('portName', 'N/A'),
                        'type': iface.get('interfaceType', 'N/A'),
                        'status': iface.get('status', 'N/A'),
                        'vlan': iface.get('vlanId', 'N/A'),
                        'ip': iface.get('ipv4Address', 'N/A')
                    } for iface in interfaces
                ]

    return render(request, 'dna_center_cisco/interface_list.html', context)

# View to see the logs from MongoDB
def logs_view(request):
    # Get all logs, newest first
    logs = ApiLog.objects.all().order_by('-timestamp') 
    return render(request, 'dna_center_cisco/logs.html', {'logs': logs})
