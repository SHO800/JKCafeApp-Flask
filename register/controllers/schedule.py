import atexit
import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func

from register import app
from route import Menus, Toppings, Order
from register.controllers.line_notification import send_stats_notify


def send_stats_job():
    try:
        with app.app_context():
            today_orders = Order.query.filter(
                func.date(Order.checked_out_at) == datetime.date.today()
            ).all()
            send_stats_notify(Menus, Toppings, today_orders)
    except Exception as e:
        print(e)


scheduler = BackgroundScheduler()
scheduler.add_job(func=send_stats_job, trigger="interval", minutes=60)
scheduler.start()



# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
