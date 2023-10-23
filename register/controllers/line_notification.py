import requests


def send(menues, total_value):
    line_notify_token = 'IgonTgHLOFrzFnRBUHuzNReVfP5keo8U7Z2WULQba29'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    message = f"""
【売上通知】
商品：{menues}
利益：{total_value}
"""
    data = {'message': message}
    requests.post(line_notify_api, headers=headers, data=data)
