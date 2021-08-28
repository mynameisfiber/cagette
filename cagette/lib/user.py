import requests
from lxml import html

import logging
import re
import json

from .constants import DEFAULT_URL


logger = logging.getLogger(__name__)


def get_form_params(form):
    params = {}
    for element in form.xpath(".//input[@name and @value]"):
        name = element.attrib["name"]
        value = element.attrib["value"]
        params[name] = value
    return params


def extract_data_from_login(dom):
    for candidate in dom.xpath('.//script[contains(text(), "dataPartner")]'):
        try:
            data_raw = re.search(
                r"dataPartner = (?P<data>\{[^}]+})", candidate.text, re.MULTILINE
            )
            data = json.loads(data_raw.groupdict()["data"])
            return data
        except (KeyError, ValueError):
            pass
    return None


class User(object):
    def __init__(self, partner_id, **meta):
        self.partner_id = partner_id
        self.meta = meta

    @classmethod
    def from_email_birthday(cls, email, birthday, api_url=DEFAULT_URL):
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
            return cls(**user_data)

    @property
    def name(self):
        try:
            name_raw = self.meta["name"]
            return name_raw.split("-", 1)[-1].strip()
        except KeyError:
            return str(self.partner_id)
