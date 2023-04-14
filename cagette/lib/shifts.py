import logging
import json
from datetime import datetime

import requests
from ics import Calendar, Event

from .constants import DEFAULT_URL

logger = logging.getLogger(__name__)


class Shifts(object):
    def __init__(self, user):
        self.user = user
        self.shifts: list = self._sync_shifts()

    def _sync_shifts(self, api_url=DEFAULT_URL) -> list:
        partner_id = self.user.meta.get("parent_id") or self.user.partner_id
        logger.debug(f"Syncing shifts for {partner_id}")
        shifts = requests.get(f"{api_url}/shifts/get_list_shift_partner/{partner_id}")
        try:
            return shifts.json()
        except json.JSONDecodeError:
            return []

    def to_ics(self) -> Calendar:
        calendar = Calendar()
        if not self.shifts:
            self.shifts = self._sync_shifts()
        now = datetime.now()
        for shift in self.shifts:
            event = Event(
                name=f'Cagette - {shift["shift_type"]}',
                begin=shift["date_begin"],
                end=shift["date_end"],
                description=shift.get("shift_id", ("",))[-1],
                last_modified=now,
                created=shift["date_begin"],
            )
            calendar.events.add(event)
        return calendar
