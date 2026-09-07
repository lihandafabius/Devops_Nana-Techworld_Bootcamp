import requests as re
response = re.get("https://gitlab.com/api/v4/users/lihandafabius/projects")
my_projects = response.json()
for project in my_projects:
    print(f"{project["name"]}:{project["web_url"]}")