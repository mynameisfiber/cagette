from flask import Flask, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .lib import User, Shifts

app = Flask(__name__)
limiter = Limiter(
    app, key_func=get_remote_address, default_limits=["240 per day", "60 per hour"]
)


def calendar_response_from_user(user):
    shifts = Shifts(user)
    filename = f"{user.name}.ics"
    return Response(
        shifts.to_ics(),
        headers={"Content-Disposition": f'filename="{filename}"'},
        mimetype="text/calendar",
    )


@app.route("/shifts/ics/<partner_id>")
def ics_partner_id(partner_id):
    user = User(partner_id)
    return calendar_response_from_user(user)


@app.route("/shifts/ics/<email>/<birthday>")
def ics_email_birthday(email, birthday):
    if not len(birthday) == 8:
        return "Invalid Birthday", 400

    try:
        user = User.from_email_birthday(email, birthday)
    except ValueError as e:
        return str(e), 400
    return calendar_response_from_user(user)


@app.route("/user/partnerid/<email>/<birthday>")
def user_partnerid_email_birthday(email, birthday):
    if not len(birthday) == 8:
        return "Invalid Birthday", 400

    try:
        user = User.from_email_birthday(email, birthday)
    except ValueError as e:
        return str(e), 400
    return user.partner_id


if __name__ == "__main__":
    pass
