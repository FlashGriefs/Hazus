import random
import threading
import json
import string
import requests

def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

def verify_nitro(proxy, webhook):
    try:
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=18))
        response = requests.get(f"http://discord.com/api/v9/entitlements/gift-codes/{code}", proxies={"http": proxy, "https": proxy}, timeout=5)
        response_data = response.json()
        if "limited" in response_data['message']:
            pass
        if "Unknown Gift Code" in response_data['message']:
            print(f"Invalid Code: discord.gift/{code}")
        if "application_id" in response_data['message']:
            print(f"Valid Code! discord.gift/{code}")
            data = {
            "content": f"@everyone **Valid Code:** discord.gift/{code}",
            "username": "HAZUS SHITTY SNIPER"
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(webhook, data=json.dumps(data), headers=headers, timeout=5)
    except requests.exceptions.ProxyError:
        pass
    except requests.exceptions.ReadTimeout:
        pass
    except KeyboardInterrupt:
        return
    except Exception as e:
        pass

def shitty_sniper():
    webhook = input("Enter webhook to send code to if it gets a valid one: ")
    try:
        proxies = get_proxies()
        while True:
            for proxy in proxies:
                thread = threading.Thread(target=verify_nitro, args=(proxy, webhook))
                thread.start()
    except KeyboardInterrupt:
        return