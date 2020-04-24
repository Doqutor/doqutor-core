import requests
import json
import time

'''
if len(sys.argv) != 3:
    print('Usage: %s APIEndpoint', sys.argv[0])

endpointbase = sys.argv[1]
endpoint = endpointbase + '/prod/patients'
token = sys.argv[2]
'''
endpoint = 'https://r22ltqq8m0.execute-api.ap-southeast-2.amazonaws.com/prod/patients'
token = 'Bearer eyJraWQiOiJzUEpBVjlxN1ZGOXNZS3ZoRzB3SThIOTFJcTFWXC9VSkJGWUk2Vk1ra285Yz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJmOTUyZmE3OS01YmRhLTRlOGYtOGEyZS03NDU2OTUxNjczY2QiLCJldmVudF9pZCI6ImI2MDAzYjEzLTY2NjUtNDBhMy1iNTMyLTBkMjg0YzEwMmIzMiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoicGhvbmUgb3BlbmlkIGVtYWlsIGRvcXV0b3JlXC9hcHBsaWNhdGlvbiIsImF1dGhfdGltZSI6MTU4NzY5OTQ1MiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoZWFzdC0yLmFtYXpvbmF3cy5jb21cL2FwLXNvdXRoZWFzdC0yX0N6TlVoTjA0cyIsImV4cCI6MTU4NzcwMzA1MiwiaWF0IjoxNTg3Njk5NDUyLCJ2ZXJzaW9uIjoyLCJqdGkiOiI4YmViODM5Yy1kODQ3LTQ5YjctOTM4ZC1mOGFlNjJhMjZlYTIiLCJjbGllbnRfaWQiOiIzN2Foa2I5b2R2ZnEzMnJ0ajc1NDd2Z3VmNSIsInVzZXJuYW1lIjoianVzdGluMSJ9.DejKRX77VefxfubM20vY52CEL0CjiLSfsGkmTlZ5ryHO9A5ahmfUzWP2eDnSiTfDD1NZcE5W5mt9xiO-vG4WJgKDuTgUY8NRFywhy7AYiFtCQeOdIjtuGCEuu4L-uMq-wL0YR9jos5tAVvLST-lHeGSjT0FIpkVhszkiPcs9B8tEgUKRH0CL0nq8WZCiX2daCQrfi-okhWp_GO1I4eaJl9LnDZFWTt-Iei6rBR9JyxuJUCYZNfTLsMsXIBJpDXE0toM-KmU8OIljwQGz3Wi9IMJHpyJ8A85o6rWhredr83-LZ48La2iE1w221Ms35gLqsogwiY-g6mmHFjUG2PfUnw'

response = requests.get(endpoint, headers = {"Authorization": token})
responsejson = response.json()
if 'data' not in responsejson:
    print(response, response.content)
else:
    patientslist = responsejson['data']
    #print(patientslist)
    for patient in patientslist:
        id = patient['id']
        print(id)
        response = requests.get(endpoint + '/' + id, headers = {"Authorization": token})
        print(response, response.content)
        print()
        time.sleep(2)


response.close()
