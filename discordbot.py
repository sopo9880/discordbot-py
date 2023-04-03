import discord
import openai
from discord.ext import commands
from cmath import log
from distutils.sysconfig import PREFIX
import discord
from dotenv import load_dotenv
import os
load_dotenv()

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix='*', intents=intents)

#PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

client = discord.Client()

openai.api_key = OPENAI

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command(name='질문')
async def ask_gpt(ctx, *, question):
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": question}
        ]
    )
    answer = result['choices'][0]['message']['content']
    await ctx.send(answer)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
    	await ctx.send("명령어를 찾지 못했습니다")

client.run(TOKEN)
