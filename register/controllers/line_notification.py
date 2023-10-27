import requests


def send(sum, detail):
    line_notify_token = 'IgonTgHLOFrzFnRBUHuzNReVfP5keo8U7Z2WULQba29'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    message = f"checkout: {sum}円"
    data = {'message': message}
    requests.post(line_notify_api, headers=headers, data=data)
