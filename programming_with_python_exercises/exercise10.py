import requests

repo_response = requests.get("https://api.github.com/users/lihandafabius/repos")
repositories = repo_response.json()
print(type(repositories))
for repository in repositories:
    print(repository["name"])

headers = {
    "Authorization": "Bearer your_token",
    "Accept": "application/vnd.github+json"
}
url = "https://api.github.com/users/lihandafabius/projectsV2"
project_response = requests.get(url, headers=headers)
projects = project_response.json()
print(project_response.status_code)
for project in projects:
    print(project["name"], project["url"])