#!/usr/bin/python

from django.conf import settings

import json
import requests

ENDPOINT = "https://api.alwaysdata.com/v1/"
credentials = (
    f"{settings.ALWAYSDATA_API_KEY} account={settings.ALWAYSDATA_ACCOUNT}",
    "",
)


def domain_record_add(record_type: str, name: str, value: str):
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
        timeout=(3.05, 27),
    )
    return response
