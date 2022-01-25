from google.cloud import storage
import tempfile
import os
import base64
from PIL import Image
import io 

class Storage_Central():
    client = None
    image = None
    project_id = "gcu-dissertation"   
    bucket = "gcu-dissertation"

    def __init__(self):
        self.client = storage.Client(project=self.project_id)            
        
    def getImage(self,path):
        #temp_uri = f"gs:L//{self.bucket}/{path}"
        _,temp = tempfile.mkstemp()
        try:
            blob = self.client.bucket(self.bucket).get_blob(path).download_as_string()
            bytess = io.BytesIO(blob)
            base = base64.b64encode(bytess.read()).decode("utf-8")
            return base
        except Exception as e:
            print(e)
            return None
        #try:
        #    print(path)
         #   with open(temp,"rb") as f:
         #       fl = f.read()
        #    encode_content = base64.b64encode(fl).decode("utf-8")
         #   print("here")
         #   return fl
        #except Exception as e:
         #   print(f"An error ocurred while opening the image: {e}")
          #  return None
        