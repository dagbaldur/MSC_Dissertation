import base64
from google.cloud import storage
import datetime

def save_data(event, context):
     try:
          pubsub_message = base64.b64decode(event['data'])
          devId = event['attributes']['deviceId']
          regId = event['attributes']['deviceRegistryId']
          regLoc = event['attributes']['deviceRegistryLocation']

          client = storage.Client()
          bucket = client.bucket('gcu-dissertation')
          fn,tme = file_name(regId,devId)
          target_blob = bucket.blob(fn)
          target_blob.upload_from_string(pubsub_message,content_type='image/jpeg')
          print(f"Finished uploading {fn}")
     except Exception as e:
          print(f"An error ocurred while uploading the image: {e}") 

def file_name(registry,device):
     directory = "IoT_imgs/"
     tme =  str(datetime.datetime.now())
     starttime = tme.replace('-','')
     starttime = starttime.replace(' ','')
     starttime = starttime.replace(':','')
     starttime = starttime.split('.',1)[0]
     name = registry + '-' + device + '-'
     fn = directory+name+starttime+".jpg"
     return fn,tme
