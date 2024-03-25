import colorama
import requests
from modules import clear
from modules import cprint

white = colorama.Fore.WHITE

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
        guildcount = 0
        for guild in guilds_data:
            guildcount += 1
            print(colorama.Fore.CYAN + f"Server Name: {guild['name']} | Server ID: {guild['id']}")
        print(f"{username} is in {guildcount} servers.")
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
            guildcount = 0
            for guild in guilds_data:
                guildcount += 1
                print(colorama.Fore.CYAN + f"Server Name: {guild['name']} | Server ID: {guild['id']}")
            print(f"{username} is in {guildcount} servers.")
        else:
            cprint("Invalid Token.\n", 1)
    else:
        cprint("Unexpected response from Discord API.\n", 1)
    print("")
    print(f"{white}Press enter to continue...")
    input()
    clear()