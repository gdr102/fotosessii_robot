import pytz
from datetime import datetime

def get_msk_time():
    msk_timezone = pytz.timezone("Europe/Moscow")
    now_msk = datetime.now(msk_timezone)
    return now_msk.strftime("%H.%M %d.%m.%Y")
