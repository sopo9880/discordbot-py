import discord, openai, os, time, random, asyncio
from discord.ext import commands
from cmath import log
from distutils.sysconfig import PREFIX
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
client = commands.Bot(command_prefix='*')

openai.api_key = "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"

#=============================================================

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

@client.event
async def on_ready():
    print('Bot is ready.')

#==============================================================
@client.command(name='질문', aliases=['선생님'], help='Open AI 의 답변을 가져옵니다.')
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

@client.command(name='타자연습', aliases=['타자', '연습'], help='타자를 연습할 수 있습니다.')
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
@client.command(name='주사위굴리기', aliases=['주사위'], help='1에서 원하는 숫자까지 랜덤한 수를 굴립니다.')
async def 주사위(ctx, str):
    num = str
    randnum = random.randint(1, num)  # 1이상 랜덤 숫자를 뽑음
    await ctx.send(f'결과는 {randnum} 입니다.')

#=============================================================

@client.command(name="가위바위보", aliases=['rsp'], help='봇과 가위바위보 한판!')
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

@client.command(name="반응속도", aliases=['반속'], help='반응속도를 테스트 할 수 있습니다.')
async def 반속(ctx, delay: float):
    await ctx.send("랜덤한 시간 뒤에 문자가 나오면 아무 말이나 보내주세요!")
    user_delay = delay / 1000
    random_delay = random.randint(3000, 6000) / 1000 # ms를 s 단위로 변환
    time.sleep(random_delay)

    start_time = time.time()
    await ctx.send("지금입니다!")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        message = await client.wait_for('message', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("시간 내에 반응하지 않았습니다.")
    else:
        end_time = time.time()
        response_time = (end_time - start_time - client.latency - user_delay) * 1000 # 디스코드 자체 지연시간과 사용자 지연시간을 모두 고려합니다.
        await ctx.send(f"{ctx.author.mention}의 반응속도는 {response_time:.2f}ms 입니다.")

#=============================================================

@client.command(name="사용자지연시간", aliases=['userdelay', 'ud'], help='사용자 개인의 지연시간을 측정합니다. 반응속도 테스트에 사용해주세요')
async def 사용자지연시간(ctx):
    await ctx.send("아무 말이나 두 번 입력해주세요.")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    messages = []
    try:
        for i in range(2):
            message = await client.wait_for('message', timeout=10.0, check=check)
            messages.append(message)
    except asyncio.TimeoutError:
        await ctx.send("시간 내에 반응하지 않았습니다.")
    else:
        response_time = (messages[1].created_at - messages[0].created_at).total_seconds() * 1000
        await ctx.send(f"{ctx.author.mention}의 지연시간은 {response_time:.2f}ms 입니다.")

#=============================================================

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
    	await ctx.send("명령어를 찾지 못했습니다")

client.run("MTA4NTQwNTU4NTI2NjIwMDYzNw.G_R0BJ.VfPqMTAAJWMIQLbQwS8iebRMupgmxgO0N95FYQ")
