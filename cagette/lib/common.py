import json
import logging
import re
from functools import lru_cache

import requests
from lxml import html

from .constants import DEFAULT_URL

logger = logging.getLogger(__name__)


def get_form_params(form):
    params = {}
    for element in form.xpath(".//input[@name and @value]"):
        name = element.attrib["name"]
        value = element.attrib["value"]
        params[name] = value
    return params


@lru_cache(8192)
def email_birthday_to_user_data(email, birthday, api_url=DEFAULT_URL):
    with requests.Session() as session:
        logger.debug("Getting form parameters")
        form_request = session.get(api_url)
        form_dom = html.fromstring(form_request.text)
        try:
            form_element = form_dom.xpath(".//form")[0]
        except IndexError:
            raise ValueError("Could not find login form")
        form_params = get_form_params(form_element)

        logger.debug("Doing login")
        login_params = {"login": email, "password": birthday, **form_params}
        login_request = session.post(api_url, data=login_params)
        logger.debug(f"Got login response: {login_request.status_code}")
        login_dom = html.fromstring(login_request.text)
        user_data = extract_data_from_login(login_dom)
        if user_data is None:
            logger.warning(f"Could not log user in: {email}")
            raise ValueError("Could not extract user data")
        logger.debug(f"Successfully logged in user: {email}")
        return user_data


def load_dirty_json(raw_json):
    raw_json = re.sub('parseInt\("([^"]+)", 10\)', r"\1", raw_json)
    return json.loads(raw_json)


def extract_data_from_login(dom):
    for candidate in dom.xpath('.//script[contains(text(), "partner_data")]'):
        try:
            data_raw = re.search(
                r"var partner_data = (?P<data>\{[^}]+})", candidate.text, re.MULTILINE
            )
            data_tmp = data_raw.groupdict()["data"]
            return load_dirty_json(data_tmp)
        except (KeyError, ValueError):
            pass
    return None
