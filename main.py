import colorama
import json
import time
import subprocess
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from botnuker import bot_nuker_helper
from shittysniper import shitty_sniper

def clear():
    if os.name == "nt":
        subprocess.Popen("cls", shell=True)
    else:
        print("\033c")

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
    try:
        webhook = input(colorama.Fore.RESET + "Webhook URL: ")

        if validate_webhook(webhook) is False:
                print(colorama.Fore.RED + "Invalid Webhook\n")
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
                        clear()
                        main()

            if use_proxies.lower().strip() == "n":
                try:
                    while True:
                        with ThreadPoolExecutor(max_workers=max_threads) as executor:
                            futures = [executor.submit(post_to_webhook, webhook, data, headers)]
                            for future in as_completed(futures):
                                future.result()
                except KeyboardInterrupt:
                    clear()
                    main()

            else:
                print (colorama.Fore.RED + "ERROR: PLEASE CHOOSE EITHER Y OR N")
                webhook_spammer()

        except KeyboardInterrupt:
            clear()
            main()
    except KeyboardInterrupt:
        clear()
        main()

def read_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

def validate_proxy(proxy):
    try:
        response = requests.get("https://discord.com/", proxies={"http": proxy, "https": proxy}, timeout=4)
        is_valid = response.status_code == 200
    except requests.RequestException:
        is_valid = False
    return proxy, is_valid

def validate_proxies():
    max_threads = int(input("Max Threads: "))
    print ("Validating Proxies...")
    proxies = read_proxies()
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

def webhook_deleter():
    try:
        webhook = input(colorama.Fore.RESET + "Webhook to delete: ")

        if validate_webhook(webhook) is False:
            print(colorama.Fore.RED + "Invalid Webhook\n")
            webhook_deleter()

        response = requests.delete(webhook)
        if response.status_code == 204:
            print(colorama.Fore.GREEN + "Webhook deleted successfully.\n")
            main()
        else:
            print(colorama.Fore.RED + "Failed to delete webhook - if the issue persists dm me on discord: flashgriefs\n")
            webhook_deleter()
        main()
    except KeyboardInterrupt:
        print ("")
        main()
        
def token_info():
    token = input("Token: ")
    response = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
    if response.status_code == 200:
        user_response = requests.get(f"https://discord.com/api/v9/users/@me", headers={"Authorization": token})
        user_data = user_response.json()
        username = user_data.get("username")
        bio = user_data.get("bio", "No bio set.")
        guilds_response = requests.get(f"https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": token})
        print(colorama.Fore.CYAN + f"------------{username}------------\n")
        print(colorama.Fore.CYAN + "Token Type: USER\n")
        print(colorama.Fore.CYAN + f"Bio: {bio}\n")
        print(colorama.Fore.CYAN + f"------------{username}------------\n")
        print(colorama.Fore.CYAN + f"Servers {username} is in:\n")
        guilds_data = guilds_response.json()
        for guild in guilds_data:
            print(colorama.Fore.CYAN + f"Server Name: {guild['name']}, Server ID: {guild['id']}")
    elif response.status_code == 401:
        response = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": f"Bot {token}"})
        if response.status_code == 200:
            user_response = requests.get(f"https://discord.com/api/v9/users/@me", headers={"Authorization": f"Bot {token}"})
            user_data = user_response.json()
            username = user_data.get("username")
            bio = user_data.get("bio", "No bio set.")
            guilds_response = requests.get(f"https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": f"Bot {token}"})
            print(colorama.Fore.CYAN + f"------------{username}------------\n")
            print(colorama.Fore.CYAN + "Token Type: BOT\n")
            print(colorama.Fore.CYAN + f"Bio: {bio}\n")
            print(colorama.Fore.CYAN + f"------------{username}------------\n")
            print(colorama.Fore.CYAN + f"Servers {username} is in:\n")
            guilds_data = guilds_response.json()
            for guild in guilds_data:
                print(colorama.Fore.CYAN + f"Server Name: {guild['name']}, Server ID: {guild['id']}")
        else:
            print(colorama.Fore.RED + "Invalid Token.\n")
            main()
    else:
        print(colorama.Fore.RED + "Unexpected response from Discord API.\n")
        main()
    print("")
    main()

def bot_nuker():
    bot_nuker_helper()
    main()

def shitty_nitro_sniper():
    shitty_sniper()
    print("Terminating sniper...")
    time.sleep(10)
    clear()
    main()

options = {
    1: validate_proxies,
    2: webhook_spammer,
    3: webhook_deleter,
    4: token_info,
    5: bot_nuker,
    6: shitty_nitro_sniper,
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
    print ("https://github.com/FlashGriefs/Hazus\n")
    print (colorama.Fore.YELLOW + 
"""    [1] Validate Proxies
    [2] Webhook Spammer
    [3] Webhook Deleter
    [4] Token Info
    [5] Bot Nuker (NOT FINISHED DONT USE)
    [6] Shitty Nitro Sniper (buggy lmao)""")
    try:
        choice = int(input(colorama.Fore.WHITE + "\nChoose Option: "))
        if choice in options:
            options[choice]()
        else:
            invalid_option()
    except ValueError:
        print (colorama.Fore.RED + "INVALID OPTION")
clear()
main()
