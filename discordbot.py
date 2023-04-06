import discord, openai, os, time, random, asyncio, requests
from bs4 import BeautifulSoup
from discord.ext import commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

openai.api_key = "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"

#=============================================================

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

@client.event
async def on_ready():
    print('Bot is ready.')

#==============================================================
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
#=============================================================

@client.command(name='타자연습', aliases=['타자', '연습'])
async def typing_test(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    # 랜덤 단어 리스트 생성
    word_list = ["사과", "바나나", "딸기", "오렌지", "수박", "파인애플", "포도", "배", "귤", "참외", "메론", "레몬", "라임", "자두", "복숭아", "애플망고", "망고스틴", "패션푸룻", "청포도", "고수"]
    selected_words = random.sample(word_list, 10)

    await ctx.send('타자 연습을 시작합니다. 준비되면 아무키나 입력하여 보내주세요.')
    await client.wait_for('message', check=check)

    start_time = time.time()

    correct = 0
    for i, word in enumerate(selected_words):
        await ctx.send(f'[{i+1}/10] {word}')

        try:
            msg = await client.wait_for('message', check=check, timeout=10.0)
        except:
            await ctx.send('시간이 초과되었습니다!')
            return

        if msg.content == word:
            correct += 1

    end_time = time.time()

    duration = round(end_time - start_time, 2)
    accuracy = round(correct / 10 * 100, 2)
    await ctx.send(f'타자 연습이 끝났습니다! 소요시간: {duration}초, 정확도: {accuracy}%')

#=============================================================
@client.command()
async def 주사위(ctx):
    randnum = random.randint(1, 6)  # 1이상 6이하 랜덤 숫자를 뽑음
    await ctx.send(f'주사위 결과는 {randnum} 입니다.')

#=============================================================

@client.command()
async def 가위바위보(ctx, user: str):  # user:str로 !가위바위보 다음에 나오는 메시지를 받아줌
    rps_table = ['가위', '바위', '보']
    bot = random.choice(rps_table)
    result = rps_table.index(user) - rps_table.index(bot)  # 인덱스 비교로 결과 결정
    if result == 0:
        await ctx.send(f'{user} vs {bot}  비겼습니다.')
    elif result == 1 or result == -2:
        await ctx.send(f'{user} vs {bot}  유저가 이겼습니다.')
    else:
        await ctx.send(f'{user} vs {bot}  봇이 이겼습니다.')

#=============================================================

@client.command()
async def 반속(ctx):
    await ctx.send("랜덤한 시간 뒤에 문자가 오면 아무말이나 입력해주세요!")
    await asyncio.sleep(random.randint(3, 5))
    t1 = time.perf_counter()
    await ctx.send("지금!")
    t2 = time.perf_counter()

    start_time = time.time()
    try:
        await client.wait_for('message', timeout=5.0)
    except:
        await ctx.send('아무말이나 입력하셨어야죠.. 시간이 초과되었습니다!')
        return
    
    end_time = time.time()

    #디스코드 전체 지연시간
    latency = round(client.latency)
    duration1 = round(t2 - t1)
    total_latency = latency + duration1
    
    #반응한 시간
    duration2 = round(end_time - start_time, 2)

    #결과
    result = ((duration2 - total_latency) * 1000) - 300

    await ctx.send(f'당신의 반응속도는: {result}ms')

#=============================================================

#=============================================================

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
    	await ctx.send("명령어를 찾지 못했습니다")
