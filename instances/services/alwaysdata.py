#!/usr/bin/python

from django.conf import settings

import json
import requests

from instances.constants import REQUEST_TIMEOUT


ENDPOINT = "https://api.alwaysdata.com/v1/"
credentials = (
    f"{settings.ALWAYSDATA_API_KEY} account={settings.ALWAYSDATA_ACCOUNT}",
    "",
)


def domain_record_list() -> dict | list:
    response = requests.get(
        f"{ENDPOINT}record/", auth=credentials, timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 401:
        # Happens if the IP is not allowed for the API token
        return [{"name": "", "domain": ""}]

    return response.json()


def domain_record_check(name: str) -> list:
    records = domain_record_list()
    domain = {"href": f"/v1/domain/{settings.ALWAYSDATA_DOMAIN_ID}/"}

    return [r for r in records if r["name"] == name and r["domain"] == domain]


def domain_record_add(record_type: str, name: str, value: str) -> dict:
    """
    Returns code 201 if successful.

    """

    # Checking if it already exists to avoid creating duplicates if called several times
    already_exists = domain_record_check(name)
    if len(already_exists):
        return {"warning": f"Record already found for subdomain {name}"}

    data = {
        "domain": int(settings.ALWAYSDATA_DOMAIN_ID),
        "type": record_type,
        "name": name,
        "value": value,
    }

    response = requests.post(
        f"{ENDPOINT}record/",
        auth=credentials,
        data=json.dumps(data),
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 201:
        return {"success": "subdomain successfully created"}
    else:
        return {"errors": response}


def domain_record_delete(name: str) -> dict:
    """
    Delete the record for name (and any duplicates)
    """
    records = domain_record_check(name)

    for record in records:
        address = f"{ENDPOINT}{record['href'][4:]}"
        response = requests.delete(address, auth=credentials, timeout=REQUEST_TIMEOUT)

        if response.status_code != 204:
            raise ValueError(f"Invalid response: {response.content.decode()}")

    return {"success": "subdomains deleted"}
