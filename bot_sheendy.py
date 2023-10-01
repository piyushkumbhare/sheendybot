import os
from datetime import datetime, time, timedelta
import asyncio
import random
import emoji
import json
import re

import discord
from discord import app_commands
from discord.utils import get
from discord.ext import commands, tasks

from dotenv import load_dotenv

"""
Requirements:
pip install
- emoji
- discord.py
- python-dotenv
"""

load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))

MY_ID = int(os.getenv('MY_ID'))
BOT_ID = int(os.getenv('BOT_ID'))

# BIRTHDAY_ROLE_ID = int(os.getenv('BIRTHDAY_ROLE_ID'))

# owners = [338869820776775691, 268126708413104128]
print(TOKEN)

# run_time = time(hour=0, minute=0, tzinfo=pytz.timezone("US/Pacific"))

bot = commands.Bot(command_prefix='$', owner_id = MY_ID, intents=discord.Intents.all())

# current_guild = None

def save():
    with open('users.json', 'w+') as fp:
        global enabled
        json.dump(fp=fp, obj=enabled, indent=4)

@tasks.loop(hours=1)
async def hourly():
    save()

enabled = {
    'users': []
}

@bot.event
async def on_ready():
    print("bot ready!")
    

    with open('users.json', 'r') as fp:
        global enabled
        enabled = json.load(fp)

    if(enabled == {}):
        enabled = {
            'users': []
        }

    print(enabled)

    # hourly.start()



    global has_started
    has_started = False

    global custom_emoji_toggle
    custom_emoji_toggle = False

    global usable_emojis
    usable_emojis = []

    global emoji_names
    emoji_names = []

    total_emojis = []
    for i in bot.guilds:
        total_emojis.extend(i.emojis)

    for i in total_emojis:
        if(i.is_usable() and not i.animated):
            usable_emojis.append(i)

        emoji_names.append(i)
    
    print([i.name for i in emoji_names])

    message = "Hello, these are the emojis I can use:\n"
    for i in usable_emojis:
        message += f"<:{i.name}:{i.id}> "
    
    # await channel.send(message)

    # synced = await bot.tree.sync()
    # print(f"Synced {len(synced)} commands!")

    # global own_avatar_bytes




    

@bot.tree.command(name="start-reaction", description="Re-syncs emojis and starts Shindi behavior (CURRENTLY DISABLED)")
async def start_reaction(interaction: discord.Interaction, num: int=1):
    global num_emojis
    num_emojis = num
    global custom_emoji_toggle
    message = ""
    custom_emoji_toggle = True
    if(len(interaction.guild.emojis) == 0):
        message = "\n(No custom emojis found. Defaulting to standard Discord emojis.)"
        custom_emoji_toggle = False

    global has_started
    if(has_started == False):
        await interaction.response.send_message(f"Starting reaction mayhem!" + message)
    else:
        await interaction.response.send_message(f"The bot is already active." + message)

    has_started = True    

    global usable_emojis
    usable_emojis = []

    global emoji_names
    emoji_names = []

    total_emojis = []
    for i in bot.guilds:
        total_emojis.extend(i.emojis)

    for i in total_emojis:
        if(i.is_usable() and not i.animated):
            usable_emojis.append(i)
    
        if(i.animated):
            emoji_names.append(i)
    
    print([i.name for i in emoji_names])


@bot.tree.command(name="stop-reaction", description="Stops Shindi behavior")
async def stop_reaction(interaction: discord.Interaction):
    global has_started
    if(has_started == False):
        await interaction.response.send_message(f"The bot is not reacting right now, so there's nothing to stop!")
        return

    await interaction.response.send_message(f"Terminating SheenD protocol. Start again with `/start-reaction`.")
    has_started = False    

def is_emoji_usable(emoji):
    return emoji.is_usable()


@bot.tree.command(name="shutdown", description="Shuts down the bot. Can only be called by owner.")
async def shutdown(interaction: discord.Interaction):

    called_by_owner = await bot.is_owner(interaction.user)
    if called_by_owner == True:
        await interaction.response.send_message("Shutting down... Until next time :wave:")

    else:
        await interaction.response.send_message("Only the owner can call this command! Hands off!")
        return
    
    #die
    await bot.close()


@bot.tree.command(name="sync-sheendy", description="Syncs commands. Can only be called by owner.")
async def sync_commands(interaction: discord.Interaction):
    called_by_owner = await bot.is_owner(interaction.user)
    if(called_by_owner == True):
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands!")
    else:
        await interaction.response.send_message("Only the owner can call this command! Hands off!")
    
    return

# @bot.tree.command(name="add-user", description="Add a user to Nitro bypass")
# async def add_user(interaction: discord.Interaction, user: discord.User):
#     global enabled
#     if(user.name in enabled['users']):
#         await interaction.response.send_message(f"User `{user.name}` already in list")
#         return  
#     enabled['users'].append(user.name)
#     print(f"Appended {user.name} to list")
#     print(f"Enabled List: {enabled['users']}")
#     await interaction.response.send_message(f"User `{user.name}` added successfully")
#     save()
#     return

# @bot.tree.command(name="delete-user", description="Deletes user from Nitro bypass")
# async def delete_user(interaction: discord.Interaction, user: discord.User):
#     global enabled
#     if(user.name not in enabled['users']):
#         await interaction.response.send_message("User not found in enabled list")
#         return
    
#     enabled['users'].remove(user.name)
#     print(f"Removed {user.name} from list")
#     print(f"Enabled List: {enabled['users']}")
#     await interaction.response.send_message(f"User `{user.name}` deleted successfully")
#     save()
#     return

ignorelist = ['baddies']

@bot.event
async def on_message(message: discord.message.Message):
    
    # if(message.guild.name in ignorelist):
    #     return
    user = message.author
    text = message.content
    print()
    if(message.webhook_id):
        print("webhook detected")
        return

    if(True):
        # print(f"Message from {user.name}: [{text}]")
        match = re.findall(r"(?<!<|a):([^\W\ ]*):", text)
        if(len(match) > 0):
            valid = False
            print(f"At least one emoji found in {text}")
            
            print(f"MATCHED GROUPS: {match}")
            for group in set(match):    
                global emoji_names
                for i in emoji_names:
                    if(i.name == group):
                        print(f"From: {user.id}")
                        print(f"Before: {text}")
                        text = text.replace(f":{i.name}:", f"<{'a' * i.animated}:{i.name}:{i.id}>")
                        print(f"After: {text}")
                        valid = True                        
            if(valid):
                await message.delete()
                avatar_bytes = await user.display_avatar.read()
                name = user.display_name
                webhook = await message.channel.create_webhook(name=name, avatar=avatar_bytes)
                if(len(text) > 2000):
                    await message.channel.send("*This message has too many emojis to send with a bot.*")
                await webhook.send(text)
                await webhook.delete()

    # global has_started
    # global custom_emoji_toggle
    # if(has_started == False):
    #     return

    # global num_emojis
    # for _ in range(num_emojis):
    #     if(custom_emoji_toggle == True):
    #         await message.add_reaction(random.choice(message.guild.emojis))
    #     else:
    #         try:
    #             await message.add_reaction(random.choice(list(emoji.EMOJI_DATA.keys())))
    #         except Exception as e:
    #             print(e)
    #             await message.add_reaction(random.choice(list(emoji.EMOJI_DATA.keys())))

  

# @bot.tree.command(name="impersonate", description="For the truly evil...")
# @app_commands.describe(user="user", content="Message content")
# async def impersonate(interaction: discord.Interaction, user: str,  content: str):
#     channel = interaction.channel

#     # grab self member    
#     own_member = channel.guild.get_member(BOT_ID)
#     own_displayname = own_member.nick
#     own_avatar_bytes = await own_member.display_avatar.read()    


#     # grab user's profile pic
    
#     # change own nickname/pfp to users
#     user_member = channel.guild.get_member(int(user[2:-1]))
#     user_avatar_bytes = await user_member.display_avatar.read()

#     user_nick = user_member.display_name

#     if(user_member.nick != None):
#         user_nick = user_member.nick

#     webhook = discord.Webhook.from_url("https://discord.com/api/webhooks/1128984040356184064/YkvRBIPJm2qDYKB506I9egVRwOXeepV0WpF5966_jTQf8BOkK_wO8gjcslTrgwN5w5TC", client=bot)

#     await webhook.edit(avatar=user_avatar_bytes, name=user_nick)


#     # delete interaction & send message
#     await interaction.response.send_message("` `")
#     await interaction.delete_original_response()
#     await webhook.send(content)

#     return



bot.run(TOKEN)
