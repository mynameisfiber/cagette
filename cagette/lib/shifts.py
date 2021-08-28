import requests
from ics import Calendar, Event

from .constants import DEFAULT_URL

class Shifts(object):
    def __init__(self, user):
        self.user = user
        self.shifts = None
        self._sync_shifts()

    def _sync_shifts(self, api_url=DEFAULT_URL):
        partner_id = self.user.partner_id
        shifts = requests.get(f'{api_url}/shifts/get_list_shift_partner/{partner_id}')
        self.shifts = shifts.json()

    def to_ics(self):
        calendar = Calendar()
        for shift in self.shifts:
            event = Event(
                name=f'Cagette - {shift["shift_type"]}',
                begin=shift['date_begin'],
                end=shift['date_end'],
                description=shift.get('shift_id', ('',))[-1]
            )
            calendar.events.add(event)
        return calendar

