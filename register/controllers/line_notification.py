import time

import requests


def send_order_notify(detail):
    line_notify_token = 'IgonTgHLOFrzFnRBUHuzNReVfP5keo8U7Z2WULQba29'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}

    detailStr = ""
    for item in detail.item:
        detailStr += f"\n  ・{item.menu_name}  {item.value}円\n"
        for option in item.option:
            detailStr += f"  └{option.option_name}  +{option.value}円\n"
        for coupon in item.coupon:
            detailStr += f"  └{coupon.coupon_name}  -{coupon.value}円\n"

    message = f"""

整理番号: {detail.order_id}
合計: {detail.total_value}円
内訳:{detailStr}
    """
    data = {'message': message}
    print(message)

    requests.post(line_notify_api, headers=headers, data=data)


def send_stats_notify(menus, menu_toppings, today_orders):
    line_notify_token = 'IgonTgHLOFrzFnRBUHuzNReVfP5keo8U7Z2WULQba29'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}

    today_order_details = {}
    for menu in menus.query.all():
        today_order_details[menu.menu_name] = 0
    for topping in menu_toppings.query.all():
        today_order_details[topping.topping_name] = 0

    for order in today_orders:
        for item in order.item:
            today_order_details[item.menu_name] += item.quantity
            for option in item.option:
                today_order_details[option.option_name] += option.quantity

    # 累計の英単語
    total = ""
    for key in today_order_details:
        total += f"  ・{key} {today_order_details[key]}個\n"

    message = f"""
【本日の累計販売数】
({time.strftime('%Y年%m月%d日 %H時%M分%S秒', time.localtime())}時点)
{total}
"""
    print(message)

    requests.post(line_notify_api, headers=headers, data=data)

