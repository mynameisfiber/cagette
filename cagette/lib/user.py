import logging
from functools import cached_property

from .common import email_birthday_to_user_data
from .constants import DEFAULT_URL

logger = logging.getLogger(__name__)


class User(object):
    def __init__(self, partner_id, **meta):
        self.partner_id: int = partner_id
        self.meta: dict = meta

    @classmethod
    def from_email_birthday(cls, email, birthday, api_url=DEFAULT_URL):
        logger.debug(f"Creating user from email/birthday: {email}")
        user_data = email_birthday_to_user_data(email, birthday, api_url)
        return cls(**user_data)

    @cached_property
    def name(self) -> str:
        try:
            name_raw = self.meta["name"]
            return name_raw.split("-", 1)[-1].strip()
        except KeyError:
            return str(self.partner_id)
