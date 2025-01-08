from django.conf import settings
from django.utils import timezone
import requests
import re

from instances.constants import POSTGRESQL_PLAN

AGENT = "Sites faciles SAAS"
STANDARD_ENDPOINT = "api.osc-fr1.scalingo.com"
SECNUMCLOUD_ENDPOINT = "api.osc-secnum-fr1.scalingo.com"


class Scalingo:
    def __init__(self, use_secnumcloud: bool = False):
        if use_secnumcloud:
            self.endpoint_url = f"https://{SECNUMCLOUD_ENDPOINT}/v1/"
        else:
            self.endpoint_url = f"https://{STANDARD_ENDPOINT}/v1/"
        self.agent = AGENT

        self.bearer_token = self.connect_session()
        self.bearer_token_time = timezone.now()

    ## Session-related methods
    def connect_session(self):
        """Exchanges the token for a bearer token that lasts one hour"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "user-agent": self.agent,
        }

        response = requests.post(
            "https://auth.scalingo.com/v1/tokens/exchange",
            headers=headers,
            auth=("", settings.SCALINGO_API_TOKEN),
            timeout=(3.05, 27),
        )
        return response.json()["token"]

    def check_session(self):
        """
        Renew the bearer token if it approaches the time limit
        """
        if timezone.now() - self.bearer_token_time >= timezone.timedelta(minutes=55):
            self.bearer_token = self.connect_session()
            self.bearer_token_time = timezone.now()

    ## HTTP methods
    def delete(self, query_path: str, params: dict = {}) -> int:
        """
        Makes a DELETE query to the endpoint and returns the result
        """
        self.check_session()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "user-agent": self.agent,
            "Authorization": f"Bearer {self.bearer_token}",
        }

        response = requests.delete(
            self.endpoint_url + query_path,
            headers=headers,
            params=params,
            timeout=(3.05, 27),
        )

        # Returns 204 No Content
        return response.status_code

    def get(self, query_path: str) -> dict:
        """
        Makes a GET query to the endpoint and returns the result
        """
        self.check_session()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "user-agent": self.agent,
            "Authorization": f"Bearer {self.bearer_token}",
        }

        response = requests.get(
            self.endpoint_url + query_path, headers=headers, timeout=(3.05, 27)
        )

        return response.json()

    def post(self, query_path: str, json_data: dict | None = None) -> dict:
        """
        Makes a POST query to the endpoint and returns the result
        """
        self.check_session()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "user-agent": self.agent,
            "Authorization": f"Bearer {self.bearer_token}",
        }

        if json_data:
            response = requests.post(
                self.endpoint_url + query_path,
                headers=headers,
                json=json_data,
                timeout=(3.05, 27),
            )
        else:
            response = requests.post(
                self.endpoint_url + query_path, headers=headers, timeout=(3.05, 27)
            )

        return response.json()

    ## App related methods
    def apps_list(self):
        apps = self.get("apps/")

        return sorted([x["name"] for x in apps["apps"]])

    def app_create(self, app_name: str) -> dict:
        pattern = re.compile("^([a-z0-9-]+)+$")

        if not pattern.match(app_name):
            raise ValueError(
                "app_name should contain only lowercap letters, digits and hyphens."
            )

        json_data = {
            "app": {
                "name": app_name,
            },
        }
        new_app = self.post("apps/", json_data=json_data)
        return new_app

    def app_delete(self, app_name: str) -> dict:
        params = {
            "current_name": app_name,
        }

        result = self.delete(f"apps/{app_name}", params=params)

        if result == 204:
            return {"success": "app successfully deleted"}
        else:
            return {"error": "error when deleting app"}

    def app_detail(self, app_name: str) -> dict:
        return self.get(f"apps/{app_name}")

    ## App / addon related methods
    def app_addon_detail(self, app_name: str, addon_id: str) -> dict:
        return self.get(f"apps/{app_name}/addons/{addon_id}")

    def app_addon_list(self, app_name: str) -> dict:
        return self.get(f"apps/{app_name}/addons")

    def app_addon_provision(self, app_name: str, plan="starter_plan") -> dict:
        json_data = {
            "addon": {
                "addon_provider_id": POSTGRESQL_PLAN["provider_id"],
                "plan_id": POSTGRESQL_PLAN[plan]["id"],
            }
        }

        new_addon = self.post(f"apps/{app_name}/addons", json_data=json_data)
        return new_addon

    def app_addon_remove(self, app_name: str, addon_id: str) -> dict:
        result = self.delete(f"apps/{app_name}/addons/{addon_id}")

        if result == 204:
            return {"success": "addon successfully removed"}
        else:
            return {"error": "error when removing addon"}

    ## App / environment related methods
    def app_variables(self, app_name: str) -> dict:
        return self.get(f"apps/{app_name}/variables")

    def app_variables_bulk_update(self, app_name: str, variables: list = []) -> dict:
        """
        Takes a list of dicts formatted like:
        [
            {
                "name":"RAILS_ENV",
                "value":"production"
            },{
                "name":"RACK_ENV",
                "value":"production"
            }
        ]
        """
        json_data = {"variables": variables}
        result = self.post(f"apps/{app_name}/variables", json_data=json_data)
        return result

    ## User related methods
    def user_info(self):
        user_data = self.get("users/self")

        return user_data
