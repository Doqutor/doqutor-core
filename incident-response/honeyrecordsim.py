import requests
import json
import time
import sys

def simulate(endpoint: str, token: str):
    response = requests.get(endpoint, headers = {"Authorization": token})
    responsejson = response.json()
    print(response, response.content)
    print()
    if 'data' in responsejson:
        print("Hit enter to send a get request on a patient")
        patientslist = responsejson['data']
        #print(patientslist)
        for patient in patientslist:
            input()
            id = patient['id']
            print(id)
            response = requests.get(endpoint + '/' + id, headers = {"Authorization": token})
            print(response, response.content)
            print()

    response.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} APIEndpoint AuthToken')
    else:
        endpoint = sys.argv[1]
        token = sys.argv[2]
        simulate(endpoint, token)
