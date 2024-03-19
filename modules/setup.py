import os
from modules import cprint

def setup():
    if not os.path.exists('config.ini'):
        cprint("config.ini file does not exist, creating one for you...", 3)
        with open('config.ini', 'w') as file:
            file.write("""[bot_nuker_config]
bot_token = YOUR_BOT_TOKEN
spam_message = @everyone NUKED BY https://github.com/FlashGriefs/Hazus
role_name = Hazus
channel_name = HAZUS ON TOP
dm_message = A SERVER YOU WERE IN WAS NUKED BY HAZUS NUKER https://github.com/FlashGriefs/Hazus
ban_message = NUKED BY https://github.com/FlashGriefs/Hazus
server_name = HAZUS OWNS U""")
    if not os.path.exists('proxies.txt'):
        cprint("proxies.txt file does not exist, creating one for you...", 3)
        with open('proxies.txt', 'w') as file:
            file.write("""# MAKE SURE ALL YOUR PROXIES ARE EITHER HTTP OR HTTPS
# PROXY FORMAT: (proxy ip):(proxy port)
# Example: 127.0.0.1:100""")