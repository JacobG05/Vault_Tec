# database.py
from pymongo import MongoClient
from config import MONGODB_URI, DATABASE_NAME

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

def get_server_collection(server_id):
    return {
        'users': db[f'{server_id}_users'],
        'messages': db[f'{server_id}_messages']
    }

def get_or_create_user(collections, discord_id, username, discriminator):
    user = collections['users'].find_one({'discord_id': discord_id})
    if not user:
        user = {
            'discord_id': discord_id,
            'username': username,
            'discriminator': discriminator
        }
        collections['users'].insert_one(user)
    return user

def save_message(collections, message_id, user_id, content, timestamp):
    message = {
        'message_id': message_id,
        'user_id': user_id,
        'content': content,
        'timestamp': timestamp
    }
    collections['messages'].insert_one(message)

async def backup_all_channels(guild):
    collections = get_server_collection(guild.id)
    for channel in guild.text_channels:
        messages = []
        async for message in channel.history(limit=None):
            user = get_or_create_user(
                collections,
                message.author.id,
                message.author.name,
                message.author.discriminator
            )
            messages.append({
                'message_id': message.id,
                'user_id': user['discord_id'],
                'content': message.content,
                'timestamp': message.created_at
            })
        if messages:
            collections['messages'].insert_many(messages)