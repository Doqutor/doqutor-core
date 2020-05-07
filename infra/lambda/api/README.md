# API

These lambdas perform the CRUD database operations to back the API defined through API Gateway.  
The API is structured as represented below using HTTP request notation.
The API architecture uses a REST approach, with the URI uniquely specifying resource through the format ‘collection/item’, and the HTTP request method/verb specifying the operation. This system is clear, conforms to HTTP semantics and allows all our functions to be included within the same API endpoint. This made setup and maintenance of both API Gateway and the frontend’s API interaction easier. Results are returned as JSON using the models defined in the [API schema](/infra/lib/api-schema.ts).

## API Routes

### Doctor

- GET /doctors: list all doctors
- POST /doctors: Create new doctor
- GET /doctors/{id}: Get information on doctor with given id
- PUT /doctors/{id}: Update information on doctor with given id
- DELETE /doctors/{id}: Delete doctor with given id

### Patient

- GET /patients: list all patients
- POST /patients: Create new patient
- GET /patients/{id}: Get information on patient with given id
- PUT /patients/{id}: Update information on patient with given id
- DELETE /patients/{id}: Delete patient with given id

Note: The block_user.py lambda in this folder should be in the util folder, but is here because of odd file permissions issues when deploying with cdk.
