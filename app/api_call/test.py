from requests import get

url = "http://localhost:8123/api/states/sun.sun"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmODY2NGY3MGQ1NTY0OTVkODkxYzE2NmVmNDc3NDRlYyIsImlhdCI6MTY2NzYxNzA4MSwiZXhwIjoxOTgyOTc3MDgxfQ.Zu3ZnQ0FsNu4P9RR0nF5u4zMjgVT1ily0Ntan5DjbgI",
    "content-type": "application/json"
}

response = get(url, headers=headers)
print(response.text)