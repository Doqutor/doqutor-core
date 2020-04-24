import requests
import json
import time
import sys

if len(sys.argv) != 3:
    print('Usage: %s APIEndpoint', sys.argv[0])
    print('Using hardcoded values')
    endpoint = 'https://r22ltqq8m0.execute-api.ap-southeast-2.amazonaws.com/prod/patients'
    token = 'Bearer eyJraWQiOiJzUEpBVjlxN1ZGOXNZS3ZoRzB3SThIOTFJcTFWXC9VSkJGWUk2Vk1ra285Yz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJmOTUyZmE3OS01YmRhLTRlOGYtOGEyZS03NDU2OTUxNjczY2QiLCJldmVudF9pZCI6ImUxZjBiYjA2LTMyZDYtNGY1Yi04MTI0LWNjZTU5MzRiYzVmMCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoicGhvbmUgb3BlbmlkIGVtYWlsIGRvcXV0b3JlXC9hcHBsaWNhdGlvbiIsImF1dGhfdGltZSI6MTU4NzcwMjMyMywiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoZWFzdC0yLmFtYXpvbmF3cy5jb21cL2FwLXNvdXRoZWFzdC0yX0N6TlVoTjA0cyIsImV4cCI6MTU4NzcwNTkyMywiaWF0IjoxNTg3NzAyMzIzLCJ2ZXJzaW9uIjoyLCJqdGkiOiI1ODdjMGQ1ZC02NjEyLTQ4M2UtYjZkMC0wMGU4OTQ3MGJjM2IiLCJjbGllbnRfaWQiOiIzN2Foa2I5b2R2ZnEzMnJ0ajc1NDd2Z3VmNSIsInVzZXJuYW1lIjoianVzdGluMSJ9.1ZYPNKkz1DIw5kRSd37ge4vQpdF7JpIjkrwAJHyBJZbp-ja4pYiD6g2_afwUUumXHzjCbkcUfmsfeqb26qhC0OreDP13UM5hw8aeJ8VtUANt4OYPmgUUtkxgrKLaHaq0zX1Cczb_kV1XY0Zxn7CXtYtjA_4M1m6BgcPdwZr3cT5ubvBfFdp3yRjS-TEO8v2mr3uLmjzMpRd0nb4_EuDAQR0duBkV4w8mRCHACF7qUXwQ_LC0g2XHEiUifJLh7k_nbKelP_oqRJ6UL5obOLu47nCL4SlhNo7BnK6c0NC7hkBhBw9LIvY_Ou1xcvSVZYxT86knL29_wKx9T-DRZ8Byug'
else:
    endpoint = sys.argv[1]
    token = sys.argv[2]


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
