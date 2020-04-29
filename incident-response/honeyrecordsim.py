import requests
import json
import time
import sys

# Getting a token:
# 1) Launch cognito hosted ui and change the following query parameters before logging in:
#       response_type=token
#       scope=doqutore/application
# or 2) Login using website, and retrieve token from cookies
# prepend 'Bearer ' to token

def simulate(endpoint: str, token: str):
    response = requests.get(endpoint, headers = {"Authorization": token})
    responsejson = response.json()
    print(response, response.content)
    print()
    if 'data' in responsejson:
        patientslist = responsejson['data']
        #print(patientslist)
        for patient in patientslist:
            input()
            id = patient['id']
            print(id)
            response = requests.get(endpoint + '/' + id, headers = {"Authorization": token})
            print(response, response.content)
            print()
            #time.sleep(2)

    response.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} APIEndpoint AuthToken')
    else:
        endpoint = sys.argv[1]
        token = sys.argv[2]
        simulate(endpoint, token)
