import requests
import json
import csv

# Configuration

start_date = "2024-04-07"
end_date = "2025-04-08" # not included

station_name = "P16 - Fiera via Marco Polo/Buozzi"
station_code = 116

url = f"https://mobility.api.opendatahub.com/v2/flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"
bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJtQkpEbmJCbnY2c3FNcjVLWEt6cXZWajZWZnFVLTh1NU5SSkNraU42X3VnIn0.eyJleHAiOjE3NDQxMDUxNDAsImlhdCI6MTc0NDEwMTU0MCwianRpIjoiZDcwYWNlY2UtYjM5MC00MTExLWFkZTktNmE5NThlN2E2NWVmIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLm9wZW5kYXRhaHViLmNvbS9hdXRoL3JlYWxtcy9ub2kiLCJhdWQiOlsiaXQuYnoubm9pLnZpcnR1YWwiLCJvZGgtbW9iaWxpdHktdjIiLCJpdC5iei5ub2kuY29tbXVuaXR5IiwiYWNjb3VudCJdLCJzdWIiOiIzMTRkNjRkMS1mZDAyLTQwMTUtOGNjNC1lMmY0NDhkY2QwMjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJvcGVuZGF0YWh1Yi1ib290Y2FtcC0yMDI1IiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsImRlZmF1bHQtcm9sZXMtbm9pIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJpdC5iei5ub2kudmlydHVhbCI6eyJyb2xlcyI6WyJWaXJ0dWFsVmlsbGFnZU1hbmFnZXIiXX0sIm9kaC1tb2JpbGl0eS12MiI6eyJyb2xlcyI6WyJPREhfUk9MRV9CQVNJQyJdfSwiaXQuYnoubm9pLmNvbW11bml0eSI6eyJyb2xlcyI6WyJBQ0NFU1NfR1JBTlRFRCJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwiZGVsZXRlLWFjY291bnQiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImNsaWVudElkIjoib3BlbmRhdGFodWItYm9vdGNhbXAtMjAyNSIsImNsaWVudEhvc3QiOiI0Ni4xOC4yOC4yNDIiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtb3BlbmRhdGFodWItYm9vdGNhbXAtMjAyNSIsImNsaWVudEFkZHJlc3MiOiI0Ni4xOC4yOC4yNDIifQ.SRHiX6nKBRULTp68nO-KT5PW-mcqheoCCM1IFyBljneNR3qVN9SPzrTvsxbo_VjIKOvzd0Oqs6s9H9eGjYQseYHNdo6Mt3tTd2UQ-qzaURFucXPke949BNsG1IuC-F_w84nzogaAB6pTmdcTdTRuflPw4cBoncK-S9CHfe5_Z7nkuKJPUF2Mllm6bMqydjIIxlMbiBMCdG-MHCz24_Ei1q9PJfNz-LKVrPmv6bYMFrCtgTrv3OyaiAZwJFdweAO9w1N03bONJBwV0K0UWEedk2cIqsEXsd4aOuGmacwmrg_hYpwNzNao9nXkzo9lSwAUjOc71GQR-RhpUX7SUxD20A"  # Replace with your actual token
output_file = "response.json"

# Set headers
headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}

# Perform the GET request
try:
    response = requests.get(url, headers=headers)
    print(response.headers)
    response.raise_for_status()  # Raise an error for bad status codes\
    print(response.status_code)
    data = response.json().get("data") # Parse JSON response

    for measurement in data:
        print("meas", measurement)

    with open('parking.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
        spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

    # Save to a JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Response saved to {output_file}")

except requests.RequestException as e:
    print(f"Request failed: {e}")
except json.JSONDecodeError:
    print("Response was not valid JSON.")
