import sys
import requests

server_ip = ""

selected_image = sys.argv[1]

tag, image_digest = selected_image.split("|", 1)

ports = {
    "1.0": 3000,
    "2.0": 8080,
    "3.0": 80
}

port = ports[tag]

app_url = f"http://{server_ip}:{port}/"

try:
    response = requests.get(app_url, timeout=10)

    if response.status_code == 200:
        print(f"Application {tag} is running successfully.")
        print(f"URL: {app_url}")
        print(f"Response: {response.text}")
    else:
        print(
            f"Application returned status code: "
            f"{response.status_code}"
        )
        sys.exit(1)

except requests.exceptions.RequestException as ex:
    print(f"Application is not accessible: {ex}")
    sys.exit(1)