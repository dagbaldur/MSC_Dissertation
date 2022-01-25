from google.cloud import iot_v1
from google.cloud import pubsub
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as gp_field_mask
from googleapiclient import discovery
from googleapiclient.errors import HttpError
import datetime 
import json
import ssl
import jwt
import paho.mqtt.client as mqtt

class devices():
    client = iot_v1.DeviceManagerClient()
    devices = []
    device = None
    project_id = "gcu-dissertation"
    cloud_region = "europe-west1"
    registry = "dissertation_test"
    private_key_file = ""#location of private key for MQTT
    jwt = None

    def __init__(self):
        #setting the first device
        print("started")

    
    def send_command(self,registry,device,command):
        if self.device is not None:
            path = self.client.device_path(self.project_id,self.cloud_region,registry,device)
            encoded_msg = command.encode("utf-8")
            try:
                response = self.client.send_command_to_device(
                    request = {"name":path,"binary_data":encoded_msg}
                )
                if response == "":
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Error: {e}")
                return False
        else:
            return False

    def get_device_info(self,id):
        info = {}
        print(self.device)
        if self.device.id == id:
            info["id"] = self.device.id
            info["name"] = self.device.name
            info["last_heartbeat"] = self.device.last_heartbeat_time.timestamp() if self.device.last_heartbeat_time is not None else 0
            info["last_error_time"] = self.device.last_error_time.timestamp() if self.device.last_error_time is not None else 0
            info["last_error"] = self.device.last_error_status.message
            
        return info

    def device_states(self):
        statuses = dict()
        for device in self.devices:
            info = dict()
            path = self.client.device_path(self.project_id,self.cloud_region,self.registry,device.id)
            status = self.client.get_device(request={"name":path})

            info["name"] = status.name
            info["num_id"] = status.num_id
            info["last_heartbeat"] = status.last_heartbeat_time.timestamp()
            info["last_event"] = status.last_event_time.timestamp()
            info["last_error_time"] = status.last_error_time.timestamp()
            info["last_error"] = status.last_error_status.message


            statuses[device.id] = info
            print(statuses)

        js = json.dumps(statuses)
        return js

    def set_device(self,device):
        try:
            device_path = self.client.device_path(self.project_id,self.cloud_region,self.registry,device)
            field_mask = gp_field_mask.FieldMask(
                paths=[
                    "id",
                    "name",
                    "num_id",
                    "last_heartbeat_time",
                    "last_event_time",
                    "last_state_time",
                    "last_config_ack_time",
                    "last_config_send_time",
                    "blocked",
                    "last_error_time",
                    "last_error_status",
                    "config",
                    "state",
                    "log_level",
                    "metadata",
                    "gateway_config",
                ]
            )
            device = self.client.get_device(request={"name":device_path,"field_mask":field_mask})
            self.device = device
            return device
        except Exception as e:
            print(e)
            return None

    def list_registires(self):
        parent = 'projects/' + self.project_id + '/locations/' + self.cloud_region
        #self.client.ListDeviceRegistriesRequest(self.project_id,self.cloud_region)
        registries = {}
        for idx,registry in enumerate(self.client.list_device_registries(parent=parent)):
            reg = {}
            reg['id'] = registry.id
            reg['name'] = registry.name
            registries[idx] = reg
        
        js = json.dumps(registries)
        return js

    def list_devices(self):
        parent = self.client.registry_path(self.project_id,self.cloud_region,self.registry)
        devices = {}
        
        for idx,device in enumerate(self.client.list_devices(parent=parent)):
            dev = {}
            dev['id'] = device.id
            dev['numid'] = device.num_id
            devices[idx] = dev

        js = json.dumps(devices)
        return js

    def set_registry(self,registry_id):
        self.registry = registry_id

    def get_registry(self):
        return self.registry    

    def create_jwt(self,expiration=60,algorithm='RSA256'):
        token = {
            "iat":datetime.datetime.utcnow(),
            "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration),
            "aud":self.project_id,
        }

        with open(self.private_key_file,"r") as f:#a private key must be created and available. The private key file is configured at init
            private_key = f.read()

        return jwt.encode(token,private_key,algorithm=algorithm)

