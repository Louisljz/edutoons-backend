from google.cloud import aiplatform
from google.oauth2 import service_account
import json

project_id = "edutoons-431101"
project_number = "560612016782"                 
endpoint_id = "1374264190394433536"
location = "us-central1"

credentials = service_account.Credentials.from_service_account_file(
    "./vertex_ai/edutoons-service-account.json"
)                                           

aiplatform.init(project=project_id, location=location, credentials=credentials)


with open('request.json') as f:
    data = json.loads(f.read())

endpoint = aiplatform.Endpoint(
    f"projects/{project_number}/locations/{location}/endpoints/{endpoint_id}"
)

prediction = endpoint.predict(instances=data['instances'])
print(prediction)
