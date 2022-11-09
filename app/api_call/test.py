from requests import get

url = "http://10.93.39.211:8123/api/history/period"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyNjA1ODZmMjg3YjM0M2JkYmFiN2Y4MmU3OGNjNmZiNyIsImlhdCI6MTY2NzgxMDg4OCwiZXhwIjoxOTgzMTcwODg4fQ.FjiV4F21eEgsF733vK1uSai9CX4ciA76K92y7RMnpvs",
    "content-type": "application/json",
    "filter_entity_id": "sun.sun"
}

response = get(url, headers=headers)
print(response.text)

fsd: str | None = "sdf"