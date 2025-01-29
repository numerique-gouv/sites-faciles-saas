from django.conf import settings
from django.utils import timezone
import requests
import re

from instances.constants import USER_AGENT, POSTGRESQL_PLAN, REQUEST_TIMEOUT

STANDARD_ENDPOINT = "api.osc-fr1.scalingo.com"
SECNUMCLOUD_ENDPOINT = "api.osc-secnum-fr1.scalingo.com"


class Scalingo:
    def __init__(self, use_secnumcloud: bool = False):
        if use_secnumcloud:
            self.endpoint_url = f"https://{SECNUMCLOUD_ENDPOINT}/v1/"
        else:
            self.endpoint_url = f"https://{STANDARD_ENDPOINT}/v1/"
        self.agent = USER_AGENT

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
            timeout=REQUEST_TIMEOUT,
        )

        if "token" not in response.json():
            raise ValueError("Token not found. Response contains: ", response.json())
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
            timeout=REQUEST_TIMEOUT,
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
            self.endpoint_url + query_path, headers=headers, timeout=REQUEST_TIMEOUT
        )

        return response.json()

    def post(
        self,
        query_path: str,
        json_data: dict | None = None,
        empty_response: bool = False,
    ) -> dict:
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
                timeout=REQUEST_TIMEOUT,
            )
        else:
            response = requests.post(
                self.endpoint_url + query_path, headers=headers, timeout=REQUEST_TIMEOUT
            )

        if empty_response:
            return {"status_code": response.status_code}
        else:
            return response.json()

    def put(self, query_path: str, json_data: dict | None = None) -> dict:
        """
        Makes a PUT query to the endpoint and returns the result
        """
        self.check_session()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "user-agent": self.agent,
            "Authorization": f"Bearer {self.bearer_token}",
        }

        if json_data:
            response = requests.put(
                self.endpoint_url + query_path,
                headers=headers,
                json=json_data,
                timeout=REQUEST_TIMEOUT,
            )
        else:
            response = requests.put(
                self.endpoint_url + query_path, headers=headers, timeout=REQUEST_TIMEOUT
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

    def app_deployment_list(self, app_name: str):
        return self.get(f"apps/{app_name}/deployments")

    def app_deployment_trigger(self, app_name: str, git_ref: str, source_url: str):
        # Deploy from a git repository
        json_data = {
            "deployment": {
                "git_ref": git_ref,
                "source_url": source_url,
            }
        }

        return self.post(f"apps/{app_name}/deployments", json_data=json_data)

    def app_restart(
        self,
        app_name: str,
        scope: list = ["web"],
    ):
        """
        Runs a command in a one-off container

        """
        json_data = {"scope": scope}

        result = self.post(
            f"apps/{app_name}/restart", json_data=json_data, empty_response=True
        )

        if result["status_code"] == 202:
            return {
                "status": "success",
                "message": "application successfully restarted",
            }
        else:
            return {
                "status": "error",
                "message": "error when restarting appication",
            }

    def app_run(
        self,
        app_name: str,
        command: str,
        variables: dict = {},
        size: str = "M",
        is_detached: bool = True,
    ):
        """
        Runs a command in a one-off container

        """
        json_data = {
            "command": command,
            "env": variables,
            "size": size,
            "detached": is_detached,
        }

        return self.post(f"apps/{app_name}/run", json_data=json_data)

    ## Domain related methods
    def app_domain_add(
        self,
        app_name: str,
        domain_name: str,
        is_canonical: bool = False,
        is_letsencrypt_enabled: bool = True,
    ):
        # Add a domain name to the app

        json_data = {
            "domain": {
                "name": domain_name,
                "canonical": is_canonical,
                "letsencrypt_enabled": is_letsencrypt_enabled,
            }
        }

        return self.post(f"apps/{app_name}/domains", json_data=json_data)

    ## App / environment related methods
    def app_variables(self, app_name: str) -> dict:
        return self.get(f"apps/{app_name}/variables")

    def app_variables_dict(self, app_name: str) -> dict:
        raw_variables = self.get(f"apps/{app_name}/variables")
        variables_dict = {}

        for ev in raw_variables["variables"]:
            k = ev["name"]
            v = ev["value"]
            variables_dict[k] = v

        return variables_dict

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
        result = self.put(f"apps/{app_name}/variables", json_data=json_data)
        return result

    ## User related methods
    def user_info(self):
        user_data = self.get("users/self")

        return user_data
