# API
The API is structured as represented below using HTTP request notation, with the structure repeated for the /patients resource.
The API architecture uses a REST approach, with the URI uniquely specifying resource through the format ‘collection/item’, and the HTTP request method/verb specifying the operation. This system is clear, conforms to HTTP semantics and allows all our functions to be included within the same API endpoint. This made setup and maintenance of both API Gateway and the frontend’s API interaction easier. Results are returned as JSON.

## API Routes

### Doctor
- GET /doctors: list doctor information
- POST /doctors: Create new doctor
- GET /doctors/{id}: Get information on doctor with given id
- PUT /doctors/{id}: Update information on doctor with given id
- DELETE /doctors/{id}: Delete doctor with given id


### Patient
- GET /patients: list patient information
- POST /patients: Create new patient
- GET /patients/{id}: Get information on patient with given id
- PUT /patients/{id}: Update information on patient with given id
- DELETE /patients/{id}: Delete patient with given id
