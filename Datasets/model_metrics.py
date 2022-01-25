from google.cloud import aiplatform
project_id = 'gcu-dissertation'
model_id = '570426632490188800'
location = 'europe-west4'
parent_eval = 'projects/'+project_id+'/locations/'+location+'/models/'+model_id
api_endpoint = location +'-aiplatform.googleapis.com'

client_args = { "api_endpoint" : api_endpoint}
client = aiplatform.gapic.ModelServiceClient(client_options=client_args)

evaluations = client.list_model_evaluations(parent=parent_eval)

print(evaluations)
