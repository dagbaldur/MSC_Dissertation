from google.cloud import storage
from google.cloud import firestore
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict as pr
import tempfile
import base64
import os
import datetime

def predict(event, context):
  os.environ['GRPC_DNS_RESOLVER'] = 'native'
  #modify the endpoint depending on the endpoint values in Vertex
  endpoint_location = 'europe-west4'
  endpoint_id = '3478133510655442944'
  endpoint_opt = {"api_endpoint":'europe-west4-aiplatform.googleapis.com'}#set the endpooint where the model is deployed
  model_client = aiplatform.gapic.PredictionServiceClient(client_options=endpoint_opt)#get the AI client

  storage_client = storage.Client()
  blob = storage_client.bucket(event['bucket']).get_blob(event['name'])
  img_uri = f"gs:L//{event['bucket']}/{event['name']}"

  trsh,temp_local_filename = tempfile.mkstemp()
  blob.download_to_filename(temp_local_filename)#local temporary storage for the image

  try:
    with open(temp_local_filename,"rb") as f:
      fl = f.read()
    encode_content = base64.b64encode(fl).decode("utf-8")#encode the image and send it to predict
  except Exception as e:
    print(f"An error occurred while opening the image: {e}")

  try:
    instance = pr.instance.ImageClassificationPredictionInstance(
      content = encode_content,
    ).to_value()

    instances = [instance]
    parameters = pr.params.ImageClassificationPredictionParams(
          confidence_threshold=0.5, max_predictions=5,
    ).to_value()

    endpoint = model_client.endpoint_path(project=event['bucket'],location=endpoint_location,endpoint=endpoint_id)
    response = model_client.predict(endpoint=endpoint,instances=instances,parameters=parameters)
    predictions = response.predictions
    for prediction in predictions:
      insert_firestore(event['bucket'],event['name'],dict(prediction))
  except Exception as e:
    print(f"An error occurred while trying to predict: {e}")

    
def insert_firestore(project,fn,prediction):
  confidence = prediction['confidences'][0]
  crack = True if prediction['displayNames'][0] == 'crack' else False

  data_values = fn.split('/')
  data_values = data_values[1].split('-')

  registry =  data_values[0]
  device = data_values[1]
  time = datetime.datetime.now()

  client = firestore.Client(project=project)
  doc_ref = client.collection(u'IoT_ImageList').document().set({
    u'registry':registry,
    u'device':device,
    u'filename':fn,
    u'time':time,
    u'prediction':{
      u'crack':crack,
      u'confidence':confidence
    }
  })
