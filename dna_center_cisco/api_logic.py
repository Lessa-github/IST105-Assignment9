import requests
import json
from .models import ApiLog

# Try to import credentials. If it fails, use dummies.
try:
    from .dnac_config import DNAC_URL, DNAC_USER, DNAC_PASS
except ImportError:
    DNAC_URL, DNAC_USER, DNAC_PASS = "URL_NOT_SET", "USER_NOT_SET", "PASS_NOT_SET"

# Disable SSL warnings (necessary for the Cisco sandbox)
requests.packages.urllib3.disable_warnings()

def log_action(action, result, ip=None, details=None):
    """Helper function to save logs to MongoDB."""
    try:
        ApiLog.objects.create(
            action=action,
            result=result,
            ip_address=ip,
            details=details
        )
    except Exception as e:
        # If logging fails, just print to console
        print(f"Error saving log to DB: {e}")

def get_dnac_token():
    """
    Gets an authentication token from the Cisco DNA Center.
    """
    if DNAC_USER == "USER_NOT_SET":
        log_action("Get Token", "Failure", details="dnac_config.py not found or misconfigured.")
        return None

    auth_url = f"{DNAC_URL}/dna/system/api/v1/auth/token"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(auth_url, auth=(DNAC_USER, DNAC_PASS), headers=headers, verify=False)
        response.raise_for_status() # Raise an error for bad status codes

        token = response.json().get('Token')
        if token:
            log_action("Get Token", "Success")
            return token
        else:
            log_action("Get Token", "Failure", details="Token not found in response.")
            return None

    except requests.exceptions.RequestException as e:
        log_action("Get Token", "Failure", details=str(e))
        return None

def get_device_list(token):
    """
    Gets the list of network devices.
    """
    if not token:
        log_action("List Devices", "Failure", details="Authentication token not provided.")
        return None, "Token not provided"

    device_url = f"{DNAC_URL}/dna/intent/api/v1/network-device"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}

    try:
        response = requests.get(device_url, headers=headers, verify=False)
        response.raise_for_status()

        devices = response.json().get('response', [])
        log_action("List Devices", "Success")
        return devices, None # Return data and no error message

    except requests.exceptions.RequestException as e:
        log_action("List Devices", "Failure", details=str(e))
        return None, str(e) # Return null and the error message

def get_device_interfaces(token, device_ip):
    """
    Gets the interfaces of a specific device by its IP.
    """
    if not token:
        log_action("Get Interfaces", "Failure", ip=device_ip, details="Token not provided.")
        return None, "Token not provided"

    # 1. First, find the device ID using the IP
    dev_id_url = f"{DNAC_URL}/dna/intent/api/v1/network-device?managementIpAddress={device_ip}"
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}

    try:
        response_id = requests.get(dev_id_url, headers=headers, verify=False)
        response_id.raise_for_status()
        devices = response_id.json().get('response', [])

        if not devices:
            error = "No device found with that IP."
            log_action("Get Interfaces", "Failure", ip=device_ip, details=error)
            return None, error

        device_id = devices[0].get('id')
        if not device_id:
            error = "Device ID not found in response."
            log_action("Get Interfaces", "Failure", ip=device_ip, details=error)
            return None, error

        # 2. With the ID, get the interfaces
        if_url = f"{DNAC_URL}/dna/intent/api/v1/interface/network-device/{device_id}"
        response_if = requests.get(if_url, headers=headers, verify=False)
        response_if.raise_for_status()

        interfaces = response_if.json().get('response', [])
        log_action("Get Interfaces", "Success", ip=device_ip)
        return interfaces, None

    except requests.exceptions.RequestException as e:
        error = str(e)
        log_action("Get Interfaces", "Failure", ip=device_ip, details=error)
        return None, error
