# bot.py
import discord
from discord.ext import commands
from config import TOKEN
from database import get_or_create_user, save_message, backup_all_channels, get_server_collection
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    collections = get_server_collection(message.guild.id)
    user = get_or_create_user(
        collections,
        message.author.id,
        message.author.name,
        message.author.discriminator
    )

    save_message(
        collections,
        message_id=message.id,
        user_id=user['discord_id'],
        content=message.content,
        timestamp=message.created_at
    )

    await bot.process_commands(message)

@bot.command()
async def backup(ctx):
    await ctx.send('Starting Backup Now.')
    await backup_all_channels(ctx.guild)
    await ctx.send('Backup complete!')

bot.run(TOKEN)