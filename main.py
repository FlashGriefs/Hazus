import colorama
import json
import time
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

def post_to_webhook(proxy=False, webhook=None, data=None, headers=None):
    if proxy == False:
        try:
            response = requests.post(webhook, data=json.dumps(data), headers=headers, timeout=5)
            if response.status_code == 204:
                print(colorama.Fore.GREEN + "Sent message to webhook.")
            else:
                print(colorama.Fore.RED + "Webhook is being rate limited.")
        except requests.exceptions.ProxyError:
            print (colorama.Fore.RED + f"Proxy {proxy} failed.")
        except requests.exceptions.ReadTimeout:
            print(colorama.Fore.RED + f"Proxy {proxy} Timed out.")
        except:
            print(colorama.Fore.RED + f"Unkown Error: {proxy}")
    else:
        try:
            response = requests.post(webhook, proxies={"http": proxy, "https": proxy}, data=json.dumps(data), headers=headers, timeout=4)
            if response.status_code == 204:
                print(colorama.Fore.GREEN + "Sent message to webhook.")
            else:
                print(colorama.Fore.RED + "Webhook is being rate limited.")
        except requests.exceptions.ProxyError:
            print(colorama.Fore.RED + f"Proxy {proxy} failed.")
        except requests.exceptions.ReadTimeout:
            print(colorama.Fore.RED + f"Proxy {proxy} Timed out.")
        except:
            print(colorama.Fore.RED + f"Unkown Error: {proxy}")

def webhook_spammer():
    use_proxies = input("Use Proxies? (Y/N): ")
    max_threads = int(input("Max Threads: "))
    webhook = input("Webhook URL: ")
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
                print(colorama.Fore.RED + "ERROR: NO PROXIES IN PROXIES.TXT")
                webhook_spammer()

            else:
                try:
                    while True:
                        with ThreadPoolExecutor(max_workers=max_threads) as executor:
                            futures = [executor.submit(post_to_webhook, proxy, webhook, data, headers) for proxy in proxylist]
                            for future in as_completed(futures):
                                future.result()
                except KeyboardInterrupt:
                    subprocess.Popen("cls", shell=True)
                    main()

        if use_proxies.lower().strip() == "n":
            try:
                while True:
                    with ThreadPoolExecutor(max_workers=max_threads) as executor:
                        futures = [executor.submit(post_to_webhook, webhook, data, headers)]
                        for future in as_completed(futures):
                            future.result()
            except KeyboardInterrupt:
                subprocess.Popen("cls", shell=True)
                main()

        else:
            print (colorama.Fore.RED + "ERROR: PLEASE CHOOSE EITHER Y OR N")
            webhook_spammer()

    except KeyboardInterrupt:
        subprocess.Popen("cls", shell=True)
        main()

def read_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

def validate_proxy(proxy):
    """Validate a proxy by attempting to connect to a test URL."""
    try:
        response = requests.get("https://discord.com/", proxies={"http": proxy, "https": proxy}, timeout=4)
        is_valid = response.status_code == 200
    except requests.RequestException:
        is_valid = False
    return proxy, is_valid

def validate_proxies():
    max_threads = int(input("Max Threads: "))
    print ("Validating Proxies...")
    proxies = read_proxies("proxies.txt")
    valid_proxies = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_proxy = {executor.submit(validate_proxy, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            proxy, is_valid = future.result()
            if is_valid:
                valid_proxies.append(proxy)
                print (colorama.Fore.GREEN + f"Valid proxy found: {proxy}")
            else:
                print(colorama.Fore.RED + f"Invalid proxy removed: {proxy}")

    with open("proxies.txt", 'w') as file:
        file.write("""# MAKE SURE ALL YOUR PROXIES ARE EITHER HTTP OR HTTPS
# PROXY FORMAT: (proxy ip):(proxy port)
# Example: 127.0.0.1:100\n""")
        for proxy in valid_proxies:
            file.write(proxy + '\n')
    print(colorama.Fore.GREEN + "Validated Proxies.")
    main()


options = {
    1: webhook_spammer,
    2: validate_proxies,
}

def invalid_option():
    print (colorama.FORE.RED + "INVALID OPTION")
    options.get(int(input(colorama.Fore.WHITE + "Choose Option: ")), invalid_option)

def main():
    time.sleep(0.1)
    colorama.just_fix_windows_console()
    print (colorama.Fore.RED + """
                                    ██╗░░██╗░█████╗░███████╗██╗░░░██╗░██████╗
                                    ██║░░██║██╔══██╗╚════██║██║░░░██║██╔════╝
                                    ███████║███████║░░███╔═╝██║░░░██║╚█████╗░
                                    ██╔══██║██╔══██║██╔══╝░░██║░░░██║░╚═══██╗
                                    ██║░░██║██║░░██║███████╗╚██████╔╝██████╔╝
                                    ╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝░╚═════╝░╚═════╝░""")
    print ("")
    print (colorama.Fore.YELLOW + 
"""    [1] Webhook Spammer
    [2] Validate Proxies""")
    try:
        choice = int(input(colorama.Fore.WHITE + "Choose Option: "))
        if choice in options:
            options[choice]()
        else:
            invalid_option()
    except ValueError:
        print (colorama.Fore.RED + "INVALID OPTION")

subprocess.Popen("cls", shell=True)
main()