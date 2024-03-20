import requests
from modules import cprint
from modules import get_proxies
from concurrent.futures import ThreadPoolExecutor, as_completed
import colorama

blue = colorama.Fore.BLUE
grey = colorama.Fore.LIGHTBLACK_EX
green = colorama.Fore.GREEN
white = colorama.Fore.WHITE
red = colorama.Fore.RED

def validate_webhook(webhook):
    response = requests.get(webhook)
    if response.status_code == 200:
        return True
    else:
        return False

def post_webhook(webhook, message, proxy):
    response = requests.post(webhook, {"content": f"{message}"}, proxies={"http": proxy, "https": proxy})
    if response.ok:
        cprint(f"Sent {message} to webhook.", 0)
    else:
        cprint(f"{response.status_code}", 1)

def webhook_spammer():
    try:
        webhook = input("Webhook: ")
        message = input(f"{white}Message To Spam: ")
        max_threads = int(input("Max Threads: "))
        proxylist = get_proxies()
        if validate_webhook(webhook) == False:
            cprint("Invalid Webhook", 1)
        while True:
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = [executor.submit(post_webhook, webhook, message, proxy) for proxy in proxylist]
                for future in as_completed(futures):
                    future.result()
    except KeyboardInterrupt:
        return