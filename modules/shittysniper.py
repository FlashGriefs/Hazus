import random
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        response = requests.get(f"http://discord.com/api/v9/entitlements/gift-codes/{code}", proxies={"http": proxy, "https": proxy}, timeout=3)
        response_data = response.json()
        if "limited" in response_data['message']:
            pass
        if "Unknown Gift Code" in response_data['message']:
            print(f"Invalid Code: discord.gift/{code}")
        if "application_id" in response_data['message']:
            print(f"Valid Code! discord.gift/{code}")
            response = requests.post(webhook, json={"content": f"@everyone **Valid Code:** discord.gift/{code}","username": "HAZUS SHITTY SNIPER"}, headers={"Content-Type": "application/json"}, timeout=5)
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
    max_threads = int(input("Max Threads: "))
    try:
        proxylist = get_proxies()
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            while True:
                for proxy in proxylist:
                    futures.append(executor.submit(verify_nitro, proxy, webhook))
    except KeyboardInterrupt:
        return