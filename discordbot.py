import discord
import openai
from discord.ext import commands

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix='*', intents=intents)

openai.api_key = OPENAI

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


'''
        {"role": "system", "content": "한문장으로 부탁합니다."},
        '''
