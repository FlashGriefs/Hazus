import colorama
import os
import sys
import asyncio
from modules import shitty_sniper
from modules import bot_nuker
from modules import webhook_spammer
from modules import cprint
from modules import clear
from modules import menu
from modules import config
from modules import token_info
from modules import webhook_deleter
from modules import get_proxies
from modules import validate_proxies
from modules import setup

gray = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
white = colorama.Fore.WHITE

options = {
    1: validate_proxies,
    2: webhook_spammer,
    3: webhook_deleter,
    4: token_info,
    5: bot_nuker,
    6: shitty_sniper,
    7: config,
}

def invalid_option():
    cprint("INVALID OPTION", 1)
    options.get(int(input(colorama.Fore.WHITE + "Choose Option: ")), invalid_option)

def main():
    colorama.just_fix_windows_console()
    menu()
    print (f"""
    {gray}[{cyan}1{gray}]{white} Validate Proxies               {gray}[{cyan}7{gray}]{white} Settings
    {gray}[{cyan}2{gray}]{white} Webhook Spammer
    {gray}[{cyan}3{gray}]{white} Webhook Deleter
    {gray}[{cyan}4{gray}]{white} Token Info
    {gray}[{cyan}5{gray}]{white} Bot Nuker
    {gray}[{cyan}6{gray}]{white} Shitty Nitro Sniper""")
    proxys = get_proxies()
    if not proxys:
        print ("")
        cprint("THERE ARE NO PROXIES IN PROXIES.TXT YOU MAY EXPERIENCE CRASHES!", 2)
    try:
        choice = int(input(colorama.Fore.WHITE + "\nChoose Option: "))
        if choice in options:
            options[choice]()
            main()
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
setup()
main()
