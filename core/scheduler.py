from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from .utils import generate_future_events


def start():
    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(generate_future_events, 'interval', days=1)
    scheduler.start()
