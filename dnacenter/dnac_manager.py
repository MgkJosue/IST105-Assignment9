import requests
from requests.auth import HTTPBasicAuth
import urllib3
from datetime import datetime
from pymongo import MongoClient
from django.conf import settings

# Desactivar warnings de SSL
urllib3.disable_warnings()

class DNAC_Manager:
    def __init__(self):
        self.token = None
        # Obtener configuraciones desde settings.py
        mongo_config = settings.MONGODB_CONFIG
        self.dnac_config = settings.DNAC_CONFIG
        
        # Conectar a MongoDB
        self.mongo_client = MongoClient(
            mongo_config['host'], 
            mongo_config['port']
        )
        self.db = self.mongo_client[mongo_config['database']]
        self.collection = self.db[mongo_config['collection']]
    
    def log_to_mongo(self, action, device_ip=None, status='success', details=None):
        """Guarda logs en MongoDB"""
        log_entry = {
            'timestamp': datetime.now(),
            'action': action,
            'device_ip': device_ip,
            'status': status,
            'details': details
        }
        self.collection.insert_one(log_entry)
    
    def get_auth_token(self):
        """Autenticación con DNA Center"""
        try:
            url = f"https://{self.dnac_config['host']}:{self.dnac_config['port']}/dna/system/api/v1/auth/token"
            response = requests.post(
                url,
                auth=HTTPBasicAuth(
                    self.dnac_config['username'], 
                    self.dnac_config['password']
                ),
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            self.token = response.json()['Token']
            
            # Log exitoso
            self.log_to_mongo(
                action='authentication', 
                status='success', 
                details='Token obtained successfully'
            )
            return self.token
            
        except Exception as e:
            # Log fallido
            self.log_to_mongo(
                action='authentication', 
                status='failure', 
                details=str(e)
            )
            raise e

    def get_network_devices(self):
        """Obtiene dispositivos de red"""
        if not self.token:
            self.get_auth_token()
            
        try:
            url = f"https://{self.dnac_config['host']}:{self.dnac_config['port']}/api/v1/network-device"
            headers = {"X-Auth-Token": self.token}
            response = requests.get(
                url, 
                headers=headers, 
                verify=False, 
                timeout=10
            )
            response.raise_for_status()
            devices = response.json().get('response', [])
            
            # Log exitoso
            self.log_to_mongo(
                action='list_devices', 
                status='success', 
                details=f'Retrieved {len(devices)} devices'
            )
            return devices
            
        except Exception as e:
            # Log fallido
            self.log_to_mongo(
                action='list_devices', 
                status='failure', 
                details=str(e)
            )
            raise e

    def get_device_interfaces(self, device_ip):
        """Obtiene interfaces de un dispositivo específico"""
        if not self.token:
            self.get_auth_token()
            
        try:
            # Primero obtener todos los dispositivos
            devices = self.get_network_devices()
            
            # Buscar el dispositivo por IP
            device = next(
                (d for d in devices if d.get('managementIpAddress') == device_ip), 
                None
            )
            
            if not device:
                self.log_to_mongo(
                    action='get_interfaces', 
                    device_ip=device_ip, 
                    status='failure', 
                    details='Device not found'
                )
                return None
            
            # Obtener interfaces del dispositivo
            url = f"https://{self.dnac_config['host']}:{self.dnac_config['port']}/api/v1/interface"
            headers = {"X-Auth-Token": self.token}
            params = {"deviceId": device['id']}
            
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                verify=False, 
                timeout=10
            )
            response.raise_for_status()
            interfaces = response.json().get('response', [])
            
            # Log exitoso
            self.log_to_mongo(
                action='get_interfaces', 
                device_ip=device_ip, 
                status='success', 
                details=f'Retrieved {len(interfaces)} interfaces'
            )
            return interfaces
            
        except Exception as e:
            # Log fallido
            self.log_to_mongo(
                action='get_interfaces', 
                device_ip=device_ip, 
                status='failure', 
                details=str(e)
            )
            raise e