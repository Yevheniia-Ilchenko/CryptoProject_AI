from requests import Request, Session
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KEY_DAPP_RADAR")
headers = {
    "accept": "application/json",
    "X-API-KEY": API_KEY
}

base_url = "https://apis.dappradar.com/v2/dapps/"


def get_project_data(dapp_id):
    """
        Fetches project data for a given DApp ID from the API.

        Parameters:
        - dapp_id (int): The ID of the project to fetch data for.

        Returns:
        - dict: The JSON response from the API if the request is successful.
        - None: If the request fails, returns None.
    """

    session = Session()
    session.headers.update(headers)
    url = f"{base_url}{dapp_id}"
    response = session.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


project_ids = [3, 20, 17, 100, 150]
projects = []
for dapp_id in project_ids:
    data = get_project_data(dapp_id)
    if data:
        projects.append(data)


with open("raw_data.json", "w") as f:
    json.dump(projects, f, indent=4)

