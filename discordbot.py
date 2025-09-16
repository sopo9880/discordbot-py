# 기본 모듈 및 라이브러리
from urllib import parse
import discord, openai, os, time, random, asyncio, requests, datetime, json, sys
import yt_dlp as youtube_dl
import nacl  # PyNaCl 라이브러리 추가
import configparser

# 디스코드 관련 모듈
from discord.ext import commands
from dotenv import load_dotenv

# 셀레니움 관련 모듈
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 기타 모듈
from urllib import request
import re
from urllib.parse import quote


#=======================================================================================================

import logging

# 로그 설정
log_file_path = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(filename=log_file_path, 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info('Program started')


print(sys.executable)
#=======================================================================================================

# API 키 및 토큰, 전역 변수 설정
config = configparser.ConfigParser()
config.read('config.txt', encoding='utf-8')

openai_api_key = config['API_KEYS']['openai_api_key'] # OpenAI API 키
riot_api_key = config['API_KEYS']['riot_api_key'] # Riot API 키
pubg_api_key = config['API_KEYS']['pubg_api_key'] # PUBG API 키
token = config['API_KEYS']['token'] # 디스코드 봇 토큰

cookies = config['PATH']['cookies'] # 유튜브 쿠키 파일 경로
stock_txt = config['PATH']['stock_txt'] # 주식 정보 파일 경로
gambling_txt = config['PATH']['gambling_txt'] # 도박 정보 파일 경로
log_file = config['PATH']['log_txt'] # 로그 파일 경로
ffmpeg_path = config['PATH']['ffmpeg_path'] # FFmpeg 경로

attitude = config['VAR']['attitude'] # 봇 활동 상태
co_pr = config['VAR']['co_pr'] # 봇 접두사

ALLOWED_USERS = config['VAR']['ALLOWED_USERS'] # 허용된 사용자
ADMIN_USERS = config['VAR']['ADMIN_USERS'] # 관리자 사용자

#=======================================================================================================

# Suppress noise about console usage from errors / 노래봇 관련
youtube_dl.utils.bug_reports_message = lambda: ''

# 환경 변수 로드
load_dotenv()

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용에 접근할 권한 부여

client = commands.Bot(command_prefix=co_pr, intents=intents)

options = Options()
options.add_argument('--headless') # 헤드리스 모드
options.add_argument('--disable-gpu') # GPU 사용 안함

ydl_opts = {
    'format': 'best',
    'cookiefile': cookies,
    'outtmpl': '%(title)s.%(ext)s',
    'noplaylist': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ydl_opts)

# 플레이리스트 설정
playlist = []

# 서버별 플레이리스트 설정
playlists = {}
# 서버별 음성 클라이언트 설정
voice_clients = {}
# 서버별 재생 상태 설정
is_playing = {}

# 현재 재생 중인지 확인하는 변수
is_playing = False

system_start_time = 0

#=======================================================================================================

@client.event
async def on_ready():
    global system_start_time
    system_start_time = time.time()
    print(f'Logged in as {client.user}')
    user = await client.fetch_user(ADMIN_USERS)
    await user.send(f'봇이 로그인되었습니다! {client.user.name}가 성공적으로 시작되었습니다.')
    await client.change_presence(activity=discord.Game(name=attitude))

#=======================================================================================================

restricted_commands = []

# 명령어 카테고리 설정
command_categories = {
    '투자': ['계좌개설', '주가', '네이버주가', '매수', '매도', '전량매도', '잔액', '보유', '포트폴리오', '파산', '장시간', '리더보드', '기록'],
    '음악': ['clear', 'pause', 'play', 'playlist', 'resume', 'search', 'skip', 'stop', 'volume'],
    '기타': ['안녕', '질문', '타자연습', '주사위굴리기', '가위바위보', '반응속도', '사용자지연시간'],
    '관리자': ['관리자', '추가', '재시작', '종료', '제한', '해제', '설정수정', '설정확인', '전체설정'],
    '전적': ['롤전적', '배그무기', '배그전적']
}

# 관리자용 명령어

@client.command(name='관리자', hidden=True)
async def 관리자(ctx):
    if str(ctx.author.id) in ALLOWED_USERS:
        embed = discord.Embed(title="관리자 명령어", color=0x000000)
        embed.add_field(name="재시작", value="봇을 재시작합니다.", inline=False)
        embed.add_field(name="종료", value="봇을 종료합니다.", inline=False)
        embed.add_field(name="제한", value="명령어를 제한합니다.", inline=False)
        embed.add_field(name="제한목록", value="제한된 명령어를 확인합니다.", inline=False)
        embed.add_field(name="해제", value="명령어를 해제합니다.", inline=False)
        embed.add_field(name="추가", value="관리자를 추가합니다.", inline=False)
        embed.add_field(name="설정수정", value="설정을 수정합니다.", inline=False)
        embed.add_field(name="설정확인", value="설정을 확인합니다.", inline=False)
        embed.add_field(name="전체설정", value="전체 설정을 확인합니다.", inline=False)
        embed.add_field(name="동작시간", value="봇이 동작한 시간을 확인합니다.", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='추가', hidden=True)
async def 추가(ctx, name: str):
    if str(ctx.author.id) in ALLOWED_USERS:
        user = discord.utils.get(ctx.guild.members, name=name)
        if user:
            if user.id in ALLOWED_USERS:
                await ctx.send(f'{user.name}님은 이미 추가되어 있습니다.')
            else:
                ALLOWED_USERS.append(user.id)
                await ctx.send(f'{user.name}님이 추가되었습니다.')
        else:
            await ctx.send(f'{name}님을 찾을 수 없습니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='재시작', hidden=True)
async def restart(ctx):
    if str(ctx.author.id) in ALLOWED_USERS:
        await ctx.send('재시작 중...')
        os.execv(sys.executable, ['python'] + sys.argv)
        await ctx.send('재시작이 완료되었습니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='종료', hidden=True)
async def shutdown(ctx):
    if str(ctx.author.id) in ALLOWED_USERS:
        await ctx.send('종료 중...')
        await client.close()
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='제한', hidden=True)
async def 제한(ctx, command_name: str):
    if str(ctx.author.id) in ALLOWED_USERS:
        if command_name in command_categories:
            for cmd in command_categories[command_name]:
                if cmd not in restricted_commands:
                    restricted_commands.append(cmd)
            await ctx.send(f'{command_name} 카테고리의 명령어를 제한합니다.')
        elif command_name not in restricted_commands:
            restricted_commands.append(command_name)
            await ctx.send(f'{command_name} 명령어를 제한합니다.')
        else:
            await ctx.send(f'{command_name} 명령어는 이미 제한되어 있습니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='제한목록', hidden=True)
async def 제한목록(ctx):
    if str(ctx.author.id) in ALLOWED_USERS:
        embed = discord.Embed(title="제한된 명령어", color=0x000000)
        for cmd in restricted_commands:
            embed.add_field(name=cmd, value='제한', inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='해제', hidden=True)
async def 해제(ctx, command_name: str):
    if str(ctx.author.id) in ALLOWED_USERS:
        if command_name in command_categories:
            for cmd in command_categories[command_name]:
                if cmd in restricted_commands:
                    restricted_commands.remove(cmd)
            await ctx.send(f'{command_name} 카테고리의 명령어를 해제합니다.')
        elif command_name in restricted_commands:
            restricted_commands.remove(command_name)
            await ctx.send(f'{command_name} 명령어를 해제합니다.')
        else:
            await ctx.send(f'{command_name} 명령어는 이미 해제되어 있습니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

# config 파일 수정 함수
def update_config(section, key, value):
    config.set(section, key, value)
    with open('config.txt', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

@client.command(name='설정수정', hidden=True)
async def update_setting(ctx, section: str, key: str, value: str):
    if str(ctx.author.id) in ALLOWED_USERS:
        update_config(section, key, value)
        await ctx.send(f'{section} 섹션의 {key} 값이 {value}로 변경되었습니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='설정확인', hidden=True)
async def check_setting(ctx, section: str, key: str = None):
    if str(ctx.author.id) in ALLOWED_USERS:
        if key == None:
            embed = discord.Embed(title=f'{section} 섹션', color=0x000000)
            for key in config[section]:
                value = config[section][key]
                embed.add_field(name=key, value=value, inline=False)
            await ctx.send(embed=embed)
        else:
            value = config[section][key]
            await ctx.send(f'{section} 섹션의 {key} 값은 {value}입니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='전체설정', hidden=True)
async def check_all_settings(ctx):
    if str(ctx.author.id) in ALLOWED_USERS:
        for section in config.sections():
            section_data = config[section]
            embed = discord.Embed(title=f'{section} 섹션', color=0x000000)
            for key, value in section_data.items():
                embed.add_field(name=key, value=value, inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

@client.command(name='동작시간', hidden=True)
async def uptime(ctx):
    if str(ctx.author.id) in ALLOWED_USERS:
        uptime = time.time() - system_start_time
        years = uptime // (365 * 24 * 3600)
        months = uptime // (30 * 24 * 3600)
        days = uptime // (24 * 3600)
        hours = (uptime % (24 * 3600)) // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        if years > 0:
            await ctx.send(f'봇이 동작한 시간은 {years:,.0f}년 {months:,.0f}개월 {days:,.0f}일 {hours:,.0f}시간 {minutes:,.0f}분 {seconds:,.0f}초 입니다.')
        elif months > 0:
            await ctx.send(f'봇이 동작한 시간은 {months:,.0f}개월 {days:,.0f}일 {hours:,.0f}시간 {minutes:,.0f}분 {seconds:,.0f}초 입니다.')
        elif days > 0:
            await ctx.send(f'봇이 동작한 시간은 {days:,.0f}일 {hours:,.0f}시간 {minutes:,.0f}분 {seconds:,.0f}초 입니다.')
        elif hours > 0:
            await ctx.send(f'봇이 동작한 시간은 {hours:,.0f}시간 {minutes:,.0f}분 {seconds:,.0f}초 입니다.')
        elif minutes > 0:
            await ctx.send(f'봇이 동작한 시간은 {minutes:,.0f}분 {seconds:,.0f}초 입니다.')
        else:
            await ctx.send(f'봇이 동작한 시간은 {seconds:,.0f}초 입니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

#=======================================================================================================

@client.command(name='기타', help='기타 명령어를 확인합니다.')  # 기타 명령어
async def 기타(ctx):
    embed = discord.Embed(title="기타 명령어", color=0xffffff)
    embed.add_field(name="안녕 or 안녕하세요 or ㅎㅇ or 하이", value="봇이 인사를 합니다. 사용법 : *안녕", inline=False)
    embed.add_field(name="질문 or 선생님", value="질문에 대한 답변을 합니다. 사용법 : *질문 [질문]", inline=False)
    embed.add_field(name="타자연습 or 타자 or 연습", value="타자연습을 할 수 있습니다. 사용법 : *타자연습", inline=False)
    embed.add_field(name="주사위굴리기 or 주사위", value="주사위를 굴립니다. 사용법 : *주사위 [숫자]", inline=False)
    embed.add_field(name="가위바위보 or rsp", value="가위바위보 게임을 할 수 있습니다. 사용법 : *가위바위보 [가위/바위/보]", inline=False)
    embed.add_field(name="반응속도 or 반속", value="반응속도를 측정합니다. 사용법 : *반응속도 [지연시간]", inline=False)
    embed.add_field(name="사용자지연시간 or userdelay or ud", value="사용자의 지연시간을 측정합니다. 사용법 : *사용자지연시간", inline=False)
    
    if ctx.author.id in ALLOWED_USERS:
        embed.add_field(name="활동상태 (권한필요)", value="봇의 활동 상태를 변경합니다.", inline=False)
        embed.add_field(name="잔액추가 (권한필요)", value="잔액을 추가합니다.", inline=False)
        embed.add_field(name="접두사 (권한필요)", value="접두사를 변경합니다.", inline=False)
    await ctx.send(embed=embed)

@client.command(name='안녕', aliases=['안녕하세요', 'ㅎㅇ', '하이'], hidden=True)
async def hello(ctx):
    await ctx.send(f"{ctx.author} | {ctx.author.mention}, 안녕하세요!")

@client.command(name='활동상태', aliases=['상태', '활동'], hidden=True)
async def activity(ctx, *, status):
    if str(ctx.author.id) not in ALLOWED_USERS:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

    global attitude
    attitude = status
    await client.change_presence(activity=discord.Game(name=attitude))
    await ctx.send(f'활동 상태가 변경되었습니다.')

@client.command(name='접두사', aliases=['prefix'], hidden=True)
async def prefix(ctx, new_prefix):
    if str(ctx.author.id) not in ALLOWED_USERS:
        await ctx.send(f'{ctx.author.mention}님은 이 명령어를 사용할 권한이 없습니다.')

    client.command_prefix = new_prefix
    await ctx.send(f'접두사가 변경되었습니다.')

#=======================================================================================================

@client.command(name='질문', aliases=['선생님'], hidden=True)
async def ask_gpt(ctx, *, question):
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": question}
        ]
    )
    answer = result['choices'][0]['message']['content']
    await ctx.send(f"{ctx.author.mention}님, 제가 생각하는 답변은 다음과 같습니다.\n {answer}")

#=======================================================================================================

@client.command(name='타자연습', aliases=['타자', '연습'], hidden=True)
async def typing_test(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

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

#=======================================================================================================

@client.command(name='주사위굴리기', aliases=['주사위'], hidden=True)
async def 주사위(ctx, str):
    num = int(str)
    randnum = random.randint(1, num)
    await ctx.send(f'결과는 {randnum} 입니다.')

#=======================================================================================================

@client.command(name="가위바위보", aliases=['rsp'], hidden=True)
async def 가위바위보(ctx, user: str):
    rps_table = ['가위', '바위', '보']
    bot = random.choice(rps_table)
    result = rps_table.index(user) - rps_table.index(bot)
    if result == 0:
        await ctx.send(f'{user} vs {bot}  비겼습니다.')
    elif result == 1 or result == -2:
        await ctx.send(f'{user} vs {bot}  유저가 이겼습니다.')
    else:
        await ctx.send(f'{user} vs {bot}  봇이 이겼습니다.')

#=======================================================================================================

@client.command(name="반응속도", aliases=['반속'], hidden=True)
async def 반속(ctx, delay: float):
    await ctx.send("랜덤한 시간 뒤에 문자가 나오면 아무 말이나 보내주세요!")
    user_delay = delay / 1000
    random_delay = random.randint(3000, 6000) / 1000
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
        response_time = (end_time - start_time - client.latency - user_delay) * 1000
        await ctx.send(f"{ctx.author.mention}의 반응속도는 {response_time:.2f}ms 입니다.")

#=======================================================================================================

@client.command(name="사용자지연시간", aliases=['userdelay', 'ud'], hidden=True)
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

#=======================================================================================================
@client.command(name="전적", help="전적 관련 명령어를 확인합니다.")
async def 전적(ctx):
    embed = discord.Embed(title="전적 관련 명령어", color=0x0000ff)
    embed.add_field(name="롤전적 or lol_Re", value="롤 전적을 확인합니다. 사용법: *롤전적 [소환사명] [태그] [갯수]", inline=False)
    embed.add_field(name="배그무기", value="배그 무기 기록을 확인합니다. 사용법: *배그무기 [닉네임]", inline=False)
    embed.add_field(name="배그전적", value="배그 전적을 확인합니다. 사용법: *배그전적 [닉네임] [개수]", inline=False)
    await ctx.send(embed=embed)


@client.command(name="롤전적", aliases=['lol_Re'], hidden=True)
async def 롤전적(ctx, *, player_info_num):
    input_str = player_info_num.split()
    if len(input_str) < 3:
        await ctx.send("사용법: *롤전적 [소환사명] [태그] [갯수]")
        return

    player_name = input_str[0]
    player_tag = input_str[1]
    try:
        num = int(input_str[2])
    except ValueError:
        await ctx.send("갯수는 숫자로 입력해주세요.")
        return

    puuid = get_puuid(player_name, player_tag)
    
    if not puuid:
        await ctx.send("소환사 정보를 가져올 수 없습니다. op.gg를 이용해주세요.")
        return
    
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={num}&api_key={riot_api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        match_ids = response.json()
    else:
        await ctx.send("전적 정보를 가져올 수 없습니다. op.gg를 이용해주세요.")
        return

    for idx, match_id in enumerate(match_ids):
        url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={riot_api_key}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            info = data['info']
            participants = info['participants']
            
            game_mode = get_game_mode(info['queueId'])
            teamKills = 0
            for participant in participants:
                if participant['puuid'] == puuid:
                    teamId = participant['teamId']
                                
                    for team in data['info']['teams']:
                        if team['teamId'] == teamId:
                            teamKills = team["objectives"]["champion"]["kills"]
                    champ_name_e = participant['championName']
                    champ_name_k = get_champion_name(champ_name_e)
                    game_duration = info['gameDuration']
                    win = participant['win']
                    kda = f"{participant['kills']} / {participant['deaths']} / {participant['assists']}"

                    double_kill = participant['doubleKills']
                    triple_kill = participant['tripleKills']
                    quadra_kill = participant['quadraKills']
                    penta_kill = participant['pentaKills']

                    champ_image_url = get_champion_image_url(champ_name_e)

                    if participant['deaths'] == 0:
                        kda_ratio = "Perfect"
                    else:
                        kda_ratio = round((participant['kills'] + participant['assists']) / participant['deaths'], 2)

                    kill_involvement = (participant['kills'] + participant['assists']) / teamKills * 100

                    cs = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
                    cs_str = round(cs / (game_duration/60), 1)

                    spells = [get_spell_name(participant['summoner1Id']), get_spell_name(participant['summoner2Id'])]

                    primary_perk = get_rune_name(get_primary_perk(participant))

                    min = game_duration // 60
                    sec = game_duration % 60

                    time_ago = datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(info['gameCreation']/1000.0)
                    time_ago_str = get_time_ago_str(time_ago)
                    
                    match_info = (f"{game_mode} {'승리' if win else '패배'} {min}분 {sec}초 \n "
                                f"{champ_name_k}  {kda} \t\t\t 평점 {kda_ratio}:1\n"
                                f" \t\t\t 킬관여 {kill_involvement:,.1f}% CS{cs} ({cs_str})\n"
                                f"더블킬:{double_kill} 트리플킬: {triple_kill} 쿼드라킬: {quadra_kill}, 펜타킬: {penta_kill}\n"
                                f"스펠: {', '.join(spells)}\n"
                                f"룬: {primary_perk}\n"
                                f"플레이 날짜: {time_ago_str}")
                    
                    embed = discord.Embed(title=f"{player_name}#{player_tag}님의 최근 {num}판 전적", color=random.randint(0, 0xffffff))
                    embed.add_field(name=f"**Match {idx+1}**", value=match_info, inline=False)
                    embed.set_thumbnail(url=champ_image_url)
                    await ctx.send(embed=embed)
                    break

#=======================================================================================================

def get_champion_name(champion_id):
    response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{get_version()}/data/ko_KR/champion.json")
    response_json = response.json()
    if 'data' in response_json and champion_id in response_json['data']:
        champion_name = response_json['data'][champion_id]['name']
        return champion_name
    else:
        return champion_id

def get_puuid(summoner_name, summoner_tag):
    url = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}?api_key={riot_api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['puuid']
    else:
        return None

REGION = 'KR'

def get_profile_icon(name, tag):
    PUUID = get_puuid(name, tag)
    url = f"https://{REGION}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{PUUID}?api_key={riot_api_key}"
    response = requests.get(url)
    summoner_data = response.json()
    if 'profileIconId' in summoner_data:
        icon_id = summoner_data['profileIconId']
        return f"http://ddragon.leagueoflegends.com/cdn/{get_version()}/img/profileicon/{icon_id}.png"
    else:
        return "Profile icon not found"

def get_game_mode(queue_id: int) -> str:
    game_modes = {
        0: "커스텀 게임",
        2: "일반 게임",
        4: "랭크 게임",
        6: "봇 게임",
        7: "솔로 랭크",
        8: "3:3 랭크",
        9: "실험 모드",
        14: "초대 봇",
        16: "초대 커스텀 봇",
        17: "아라모드",
        25: "일반 5:5 드래프트",
        31: "봇 협동",
        32: "봇 인트로",
        33: "봇 중간",
        41: "3:3 랭크",
        42: "트리니티 포스",
        52: "ARAM (학원 시험)",
        61: "블리츠",
        65: "격전",
        70: "일반 모드",
        76: "그림자 늪",
        78: "울프 워프",
        83: "돌격 넥서스",
        91: "티어즈",
        92: "빌기워터",
        93: "U.R.F",
        94: "파괴자의 조각",
        96: "블리츠모드",
        98: "별수호자",
        100: "일반 3:3 블라인드",
        300: "일반 우주 봇",
        400: "일반",
        420: "솔로 랭크",
        430: "일반",
        440: "자유 5:5 랭크",
        450: "무작위 총력전",
        460: "스페셜 3:3 블라인드",
        470: "스페셜 3:3 드래프트",
        600: "블랙마켓",
        610: "AI 정글",
        700: "소환사의 협곡 5:5 랭크",
        720: "우르프(URF)",
        800: "커스텀 게임",
        810: "초대 봇",
        820: "초대 커스텀 봇",
        830: "초대 봇 인트로",
        840: "초대 봇 쉬움",
        850: "초대 봇 일반",
        870: "초대 봇 인트로",
        880: "초대 봇 쉬움",
        890: "초대 봇 일반",
        900: "무작위 URF",
        910: "승천",
        920: "왕의 전설",
        940: "넥서스 공성전",
        950: "둠 봇 투표",
        960: "둠 봇 표준",
        980: "스타 가디언 일반",
        990: "스타 가디언 돌격",
        1000: "프로젝트: 헌터스",
        1010: "눈의 ARURF",
        1020: "하나를 위한 모두",
        1030: "오디세이 추출: 인트로",
        1040: "오디세이 추출: 카드",
        1050: "오디세이 추출: 크루멤버",
        1060: "오디세이 추출: 캡틴",
        1070: "오디세이 추출: 돌격",
        1090: "전투 전략",
        1100: "랭크 전투 전략",
        1110: "전투 전략 튜토리얼",
        1111: "전투 전략 테스트",
        1200: "넥서스 블리츠",
        1210: "전투 전략: 촹크의 보물 모드",
        1300: "넥서스 블리츠",
        1400: "궁극의 스펠북",
        1700: "아레나",
        1710: "아레나 (16 플레이어 로비)",
        1810: "스웜 모드 (1 플레이어)",
        1820: "스웜 모드 (2 플레이어)",
        1830: "스웜 모드 (3 플레이어)",
        1840: "스웜 모드 (4 플레이어)",
        1900: "픽 URF",
        2000: "튜토리얼 1",
        2010: "튜토리얼 2",
        2020: "튜토리얼 3"
    }
    if queue_id in game_modes:
        return game_modes[queue_id]
    else:
        return "알 수 없는 게임 모드입니다."


def get_spell_name(summoner_spell_id):
    response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{get_version()}/data/ko_KR/summoner.json")
    response_json = response.json()
    for spell in response_json['data'].values():
        if spell['key'] == str(summoner_spell_id):
            return spell['name']
    return 'Unknown'

def get_primary_perk(participant):
    primary_style = participant['perks']['styles'][0]
    for selection in primary_style['selections']:
        if selection['perk'] != 0:
            return selection['perk']
    return None

def get_rune_name(rune_id):
    response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{get_version()}/data/ko_KR/runesReforged.json")
    response_json = response.json()
    for tree in response_json:
        for slot in tree['slots']:
            for rune in slot['runes']:
                if rune['id'] == rune_id:
                    return rune['name']
    return 'Unknown'

def get_time_ago_str(delta):
    delta_min = delta.total_seconds() // 60
    if delta_min < 60:
        return f"{int(delta_min)}분 전"
    elif delta_min < 1440:
        return f"{int(delta_min//60)}시간 전"
    else:
        return f"{int(delta_min//1440)}일 전"

def download_image(url, filename):
    with open(filename, 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print(f"Error: {response.status_code} - {response.text}")

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

def get_champion_image_url(champion_name):
    version = get_version()
    response = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json')
    champions = response.json()['data']

    for champ in champions.values():
        if champ['id'] == champion_name:
            url = f"http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ['image']['full']}"
            return url

def get_team_kills(match_id, team_id):
    match_data = get_match_data(match_id)
    team_kills = 0
    for participant in match_data["info"]["participants"]:
        if participant["teamId"] == team_id:
            team_kills += participant["kills"]
    return team_kills

def get_match_data(match_id):
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={riot_api_key}'
    response = requests.get(url)
    return response.json()

def get_version():
    response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if response.status_code == 200:
        versions = response.json()
        return versions[0]

#=======================================================================================================

def fetch_tft_data(puuid, count):
    # 매치 리스트 가져오기
    match_list_url = f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={riot_api_key}"
    match_list_response = requests.get(match_list_url)
    match_list = match_list_response.json()

    match_data = []
    for match_id in match_list:
        # 각 매치의 상세 정보 가져오기
        match_url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key={riot_api_key}"
        match_response = requests.get(match_url)
        match_details = match_response.json()
        print(match_details)
        # 필요한 정보 추출
        for participant in match_details['info']['participants']:
            if participant['puuid'] == puuid:
                data = {
                    "rank": participant['placement'],
                    "used_champions": [unit['character_id'] for unit in participant['units']],
                    "last_stage": f"{participant['last_round']//10}-{participant['last_round']%10}",
                    "duration": match_details['info']['game_length'],
                    "played_time": datetime.datetime.fromtimestamp(match_details['info']['game_datetime']/1000),
                    "synergies": [trait['name'] for trait in participant['traits'] if trait['tier_current'] > 0],
                    "game_mode": match_details['info']['queue_id']
                }
                match_data.append(data)
                break

    return match_data

@client.command(name='TFT전적', aliases=['tft'], hidden=True)
async def TFT전적(ctx, name: str, tag: str, count: int):
    puuid = get_puuid(name, tag)
    profile_icon_url = get_profile_icon(name, tag)
    match_data_list = fetch_tft_data(puuid, count)
    
    for data in match_data_list:
        embed = discord.Embed(title=f"{name}#{tag}의 TFT 전적", color=discord.Color.blue())
        embed.set_thumbnail(url=profile_icon_url)
        embed.add_field(name="등수", value=data["rank"], inline=False)
        embed.add_field(name="사용한 챔프", value=", ".join(data["used_champions"]), inline=False)
        embed.add_field(name="마지막 스테이지", value=data["last_stage"], inline=False)
        embed.add_field(name="걸린 시간", value=f"{data['duration'] // 60}분 {data['duration'] % 60}초", inline=False)
        embed.add_field(name="플레이한 시간", value=f"{data['played_time'].days}일 전", inline=False)
        embed.add_field(name="시너지", value=", ".join(data["synergies"]), inline=False)
        embed.add_field(name="게임 모드", value=get_game_mode(data["game_mode"]), inline=False)
        
        await ctx.send(embed=embed)
        
#=======================================================================================================
@client.command(name='배그무기', hidden=True)
async def get_weapon_stats(ctx, username):
    await ctx.send(f'{username}의 무기 기록을 검색 중입니다...')

    headers = {
        'Authorization': f'Bearer {pubg_api_key}',
        'Accept': 'application/vnd.api+json'
    }

    response = requests.get(f'https://api.pubg.com/shards/steam/players?filter[playerNames]={username}', headers=headers)
    if response.status_code != 200:
        await ctx.send('플레이어 정보를 가져오는 데 실패했습니다.')
        return

    player_id = response.json()['data'][0]['id']
    response = requests.get(f'https://api.pubg.com/shards/steam/players/{player_id}/weapon_mastery', headers=headers)
    if response.status_code != 200:
        await ctx.send('무기 마스터리 데이터를 가져오는 데 실패했습니다.')
        return

    weapon_stats = response.json()['data']['attributes']['weaponSummaries']

    # 무기, 장거리 킬, 딜량, 헤드샷, 킬수를 리스트로 만듭니다.
    weapons = []
    longest_kills = []
    damages = []
    headshots = []
    kills = []
    Groggies = []
    MostKillsInAGame = []

    for weapon, data in weapon_stats.items():
        stats = data['OfficialStatsTotal']
        weapons.append(weapon)
        longest_kills.append(stats['LongestKill'])
        damages.append(stats['DamagePlayer'])
        headshots.append(stats['HeadShots'])
        kills.append(stats['Kills'])
        Groggies.append(stats['Groggies'])
        MostKillsInAGame.append(stats['MostKillsInAGame'])

    # 리스트에서 최대 값을 가져와 비교합니다.
    longest_kill = {'weapon': weapons[longest_kills.index(max(longest_kills))], 'distance': max(longest_kills)}
    highest_damage = {'weapon': weapons[damages.index(max(damages))], 'damage': max(damages)}
    most_headshots = {'weapon': weapons[headshots.index(max(headshots))], 'headshots': max(headshots)}
    most_kills = {'weapon': weapons[kills.index(max(kills))], 'kills': max(kills)}
    most_gronggies = {'weapon': weapons[Groggies.index(max(Groggies))], 'Groggies': max(Groggies)}
    most_killsinagame = {'weapon': weapons[MostKillsInAGame.index(max(MostKillsInAGame))], 'MostKillsInAGame': max(MostKillsInAGame)}

    # 무기 이름을 한국어로 변환합니다.
    weapon_names_kr = {
        "Item_Weapon_ACE32_C": "ACE 32",
        "Item_Weapon_AK47_C": "AK47",
        "Item_Weapon_AUG_C": "AUG",
        "Item_Weapon_AWM_C": "AWM",
        "Item_Weapon_Berreta686_C" : "S686",
        "Item_Weapon_BerylM762_C": "베릴 M762",
        "Item_Weapon_BizonPP19_C": "PP-19 비존",
        "Item_Weapon_BluezoneGrenade_C": "블루존 수류탄",
        "Item_Weapon_C4_C": "C4",
        "Item_Weapon_Crossbow_C": "석궁",
        "Item_Weapon_DP12_C": "DP-12",
        "Item_Weapon_DP28_C": "DP-28",
        "Item_Weapon_DesertEagle_C": "데저트 이글",
        "Item_Weapon_Dragunov_C": "드라그노프",
        "Item_Weapon_FAMASG2_C": "FAMAS G2",
        "Item_Weapon_FNFal_C": "SLR",
        "Item_Weapon_G18_C": "G18",
        "Item_Weapon_G36C_C": "G36C",
        "Item_Weapon_Grenade_C": "수류탄",
        "Item_Weapon_Groza_C": "Groza",
        "Item_Weapon_HK416_C": "M416",
        "Item_Weapon_JS9_C": "JS9",
        "Item_Weapon_K2_C": "K2",
        "Item_Weapon_Kar98k_C": "Kar98k",
        "Item_Weapon_L6_C": "Deagle L6",
        "Item_Weapon_M16A4_C": "M16A4",
        "Item_Weapon_M1911_C": "M1911",
        "Item_Weapon_M249_C": "M249",
        "Item_Weapon_M24_C": "M24",
        "Item_Weapon_M9_C": "M9",
        "Item_Weapon_MG3_C": "MG3",
        "Item_Weapon_MP5K_C": "MP5K",
        "Item_Weapon_Mini14_C": "Mini-14",
        "Item_Weapon_Mk12_C": "Mk12",
        "Item_Weapon_Mk14_C": "Mk14",
        "Item_Weapon_Mk47Mutant_C": "Mk47 Mutant",
        "Item_Weapon_Molotov_C": "화염병",
        "Item_Weapon_Mosin_C": "모신나강",
        "Item_Weapon_NagantM1895_C": "R1895",
        "Item_Weapon_OriginS12_C": "O12",
        "Item_Weapon_PanzerFaust100M_C": "판처파우스트",
        "Item_Weapon_QBU88_C": "QBU88",
        "Item_Weapon_QBZ95_C": "QBZ95",
        "Item_Weapon_Rhino_C": "R45",
        "Item_Weapon_SCAR-L_C": "SCAR-L",
        "Item_Weapon_SKS_C": "SKS",
        "Item_Weapon_Saiga12_C": "S12K",
        "Item_Weapon_Sawnoff_C": "소드오프",
        "Item_Weapon_Thompson_C": "Tommy Gun",
        "Item_Weapon_UMP_C": "UMP",
        "Item_Weapon_UZI_C": "마이크로 UZI",
        "Item_Weapon_VSS_C": "VSS",
        "Item_Weapon_Vector_C": "벡터",
        "Item_Weapon_Win1894_C": "Win94",
        "Item_Weapon_Winchester_C": "S1897",
        "Item_Weapon_vz61Skorpion_C": "스콜피온"
    }
    # 배그 로고 URL
    pubg_logo_url = "https://i.namu.wiki/i/8u39nkUcGKgrfNnzlIhCI1JZ81t-vlG7N6sFutvfg4KCzXx0kJM0gndnntNU8FpdN3y86LC-fviiaqPTLP-715AXnNGxs38ZQ7-AZq4YVoLquWv8AyKVsbnnSBBqB0D_NyUP05Q0WbHF8wjmUWyKDw.svg"

    # embed로 출력합니다.
    embed = discord.Embed(title=f'{username}의 기록입니다!', color=0x00ff00)
    embed.set_thumbnail(url=pubg_logo_url)
    embed.add_field(name='최장거리 킬', value=f"{weapon_names_kr.get(longest_kill['weapon'], longest_kill['weapon'])}, {longest_kill['distance']}m")
    embed.add_field(name='최다 딜량', value=f"{weapon_names_kr.get(highest_damage['weapon'], highest_damage['weapon'])}, {highest_damage['damage']}")
    embed.add_field(name='최다 헤드샷', value=f"{weapon_names_kr.get(most_headshots['weapon'], most_headshots['weapon'])}, {most_headshots['headshots']}k")
    embed.add_field(name='최다 킬', value=f"{weapon_names_kr.get(most_kills['weapon'], most_kills['weapon'])}, {most_kills['kills']}k")
    embed.add_field(name='최다 기절', value=f"{weapon_names_kr.get(most_gronggies['weapon'], most_gronggies['weapon'])}, {most_gronggies['Groggies']}")
    embed.add_field(name='매치 최다 킬', value=f"{weapon_names_kr.get(most_killsinagame['weapon'], most_killsinagame['weapon'])}, {most_killsinagame['MostKillsInAGame']}k")

    await ctx.send(embed=embed)


def get_teammates(api_key, name, match_id):
    url = f'https://api.pubg.com/shards/steam/matches/{match_id}'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/vnd.api+json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f'Error: {response.status_code}'

    match_data = response.json()

    player_winplace = None
    teammates = []

    for participant in match_data['included']:
        if participant['type'] == 'participant' and participant['attributes']['stats']['name'] == name:
            player_winplace = participant['attributes']['stats']['winPlace']
            break

    if player_winplace is None:
        return 'Error: Player not found in the match'

    for participant in match_data['included']:
        if participant['type'] == 'participant' and participant['attributes']['stats']['winPlace'] == player_winplace:
            teammate_name = participant['attributes']['stats']['name']
            if teammate_name != name:
                teammates.append(teammate_name)

    return teammates

@client.command(name='배그전적', hidden=True)
async def get_stats(ctx, username, match_count: int):
    await ctx.send(f'{username}님의 최근 {match_count}판 전적을 검색 중입니다...')

    headers = {
        'Authorization': f'Bearer {pubg_api_key}',
        'Accept': 'application/vnd.api+json'
    }

    user_response = requests.get(f'https://api.pubg.com/shards/steam/players?filter[playerNames]={username}', headers=headers)

    if user_response.status_code != 200:
        await ctx.send(f'유저 정보를 가져오는 중 오류가 발생했습니다: {user_response.status_code}')
        return

    user_data = user_response.json()

    if not user_data['data']:
        await ctx.send(f'유저 {username}을(를) 찾을 수 없습니다.')
        return

    player_id = user_data['data'][0]['id']
    matches = user_data['data'][0]['relationships']['matches']['data'][:match_count]

    map_names = {
        "Baltic_Main": "에란겔",
        "Desert_Main": "미라마",
        "Savage_Main": "사녹",
        "DihorOtok_Main": "비켄디",
        "Summerland_Main": "카라킨",
        "Tiger_Main": "태이고",
        "Paramo_Main": "파라모",
        "Haven_Main": "헤이븐",
        "Kiki_Main": "데스턴",
        "Neon_Main": "론도"
    }

    map_thumbnails = {
        "에란겔": "https://i.namu.wiki/i/ZP1kCI_H3_9ZA-v-mguXhvJZfHq4UEl2U2KIRghHhMBzwNEFUX2Ut6y6K-Uc_ImtEuEudR2dx0mP-S7dJRrgObRRVeMzaNmEgDOifOa6bXKaj29e4WLZdqZgAi_Kput8LqKahI-PAeVSrg3jclblNw.webp",
        "미라마": "https://i.namu.wiki/i/fOLshjh8wm4HzRiB7vojIFsUhW3EFludqKCFWlyimVknRDMjFhv1O6MKHOLdHQ0oPnNsi_ehs158BTO-Vfd0wZLoJORG1q2A78MFYLkIIDbHCcy0ApVuZ37J_m-cYd4gSe3fgfhQEdvpdEvdAoOcXQ.webp",
        "사녹": "https://i.namu.wiki/i/kK-Glah4gjQ44weIJaRaRBGRij0jKAnlSWDNeREeHj0QTt7-JZ5Zn8QkVvcG4271rhWnT6FoIa6dlvv4NBtYGiKKesrxoXZ4ojeK-UAXPRbEUNqoN2o4DovbdMSyeD9nynlK_gxvo-vub1WYDaJ1OA.webp",
        "비켄디": "https://i.namu.wiki/i/NRo_sibKBx7QqcHwlYwX_gc13P0PDmt_GaGQ_gtjMPX9btR6mqy_77DKUgUZwYrCSrwDh52m-Fa-_2tijVN10kF2Zdank3UkVCRMyeJfR8spd-skibAG5oRQi-gJd_QNausDwDlKj6PP0Trriippnw.webp",
        "카라킨": "https://i.namu.wiki/i/nTLCFjx4ixFUSpjeaX4Za3vnLCFXuZGpY0tvbHioS6qbg_qOzI2hlFD8c3zPQy7f7jZpOc7tR35rtERL0d6WJeLtENeuKWT9RgV93n-QdihpJOUyM1-fNpLhKpwRJ00HhlWDJktkJQdis-LZgj5exg.webp",
        "태이고": "https://i.namu.wiki/i/UXQ2ywmj5O331nbQUXAE1nQNUjpBvrsMaYHHqjwRIVVIRPIE9TczB2y89wX5QnoroR1m8vsA7fD4_xtb4BWLGgTeVOc0qu5RiZ8JdSpfDTXpcTle-3gF5LUf88lQPESEh8ZpJ2-Q8D7rHcf428UpEQ.webp",
        "파라모": "https://i.namu.wiki/i/yEUO7bUTbHHl0ORCBy_cSYESzun_iu7euQ--KxzC_Ysk5jmhXEgmWM-P0PdtjGcTdSTzLIXvNcSJLWNseSlU8oCubRKxEIbex43Zavw8m3E2T-aWX1Xdzxz6AW5kRbjoV5lZ6fS_lM-IXxzA56oLqg.webp",
        "헤이븐": "https://i.namu.wiki/i/VkJtxz4pE1B_byfN6xt-cbX9WjOEtafDTZ3MSp6ZVvZYigB0Lc8-w5JZpGSHApuZ3liAkSM1dFk_VVRBVelHeZpF1nGX1oGDyY8L4qVoHbFr5CkqGpjas0x_8S1CDwobTniA6Tymro8QFHuhG62PTQ.webp",
        "데스턴": "https://i.namu.wiki/i/hCgIyr6EeeecG74ODPMxb-GxMoIcROdMpAe6nhCMJngMVP39UsdseWliliVEGfT5TQVWT9TS8gnytav07Xl0lNIzNbjFB5bPWc2MPUCoq9I32y7Z4WknVPuGv0nQmnT4ypEXOpx6Du47P7ENKWUl_w.webp",
        "론도" : "https://i.namu.wiki/i/4jPOciB2Eojm-1taWImtyVM8WBHcOX4I_rm497nOWvKNHbGcADmLeacezNaYsGzYo70jvgv6hEI67UmhC-gXmkzhdOMH7jE0Pwazb7Taz1juSEC0nVPw-r2urz86ExT91T0EgAgqkctH97kR2jh52w.webp"
    }

    for match in matches:
        match_id = match['id']
        match_response = requests.get(f'https://api.pubg.com/shards/steam/matches/{match_id}', headers=headers)

        if match_response.status_code != 200:
            await ctx.send(f'매치 {match_id} 정보를 가져오는 중 오류가 발생했습니다: {match_response.status_code}')
            continue

        match_data = match_response.json()
        attributes = match_data['data']['attributes']
        duration_seconds = attributes['duration']
        duration_minutes = duration_seconds // 60
        duration_seconds = duration_seconds % 60
        duration = f"{duration_minutes}분 {duration_seconds}초"
        map_name = map_names.get(attributes['mapName'], attributes['mapName'])
        match_start = datetime.datetime.strptime(attributes['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
        match_start = match_start + datetime.timedelta(hours=9)  # Convert to Korean time
        game_mode = attributes['gameMode']

        participant = next(p for p in match_data['included'] if p['type'] == 'participant' and p['attributes']['stats']['playerId'] == player_id)
        stats = participant['attributes']['stats']

        total_distance = stats['rideDistance'] + stats['swimDistance'] + stats['walkDistance']

        teammates = get_teammates(pubg_api_key, username, match_id)
        teammates_str = ', '.join(teammates) if teammates else '없음'

        color = discord.Color.blue()
        if stats['winPlace'] == 1:
            color = discord.Color.gold()
        elif map_name == "에란겔":
            color = discord.Color.from_rgb(39, 39, 0)
        elif map_name == "미라마":
            color = discord.Color.from_rgb(81, 37, 0)
        elif map_name == "사녹":
            color = discord.Color.from_rgb(0, 73, 0)
        elif map_name == "비켄디":
            color = discord.Color.from_rgb(0, 48, 92)
        elif map_name == "카라킨":
            color = discord.Color.from_rgb(75, 25, 0)
        elif map_name == "태이고":
            color = discord.Color.from_rgb(45, 27, 0)
        elif map_name == "파라모":
            color = discord.Color.from_rgb(26, 26, 26)
        elif map_name == "헤이븐":
            color = discord.Color.from_rgb(17, 17, 17)
        elif map_name == "데스턴":
            color = discord.Color.from_rgb(60, 15, 15)
        elif map_name == "론도":
            color = discord.Color.from_rgb(92, 2, 37)

        embed = discord.Embed(title=f'{username}님의 매치', color=color)
        embed.set_footer(text=match_start.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name='맵', value=map_name, inline=True)
        embed.add_field(name='게임모드', value=game_mode, inline=True)
        embed.add_field(name='등수', value=f"{stats['winPlace']}등", inline=True)
        embed.add_field(name='킬 수', value=f"{stats['kills']}k", inline=True)
        embed.add_field(name='어시스트', value=f"{stats['assists']}회", inline=True)
        embed.add_field(name='기절시킨 횟수', value=f"{stats['DBNOs']}회", inline=True)
        embed.add_field(name='헤드샷', value=f"{stats['headshotKills']}k", inline=True)
        embed.add_field(name='딜량', value=f"{stats['damageDealt']:.2f}", inline=True)
        embed.add_field(name='최장거리 킬', value=f"{stats['longestKill']:.2f}m", inline=True)
        embed.add_field(name='이동거리', value=f"총 이동거리: {total_distance:.2f}m", inline=False)
        embed.add_field(name='동료', value=teammates_str, inline=False)
        embed.add_field(name='매치시간', value=duration, inline=True)

        if map_name in map_thumbnails:
            embed.set_thumbnail(url=map_thumbnails[map_name])

        await ctx.send(embed=embed)

#=======================================================================================================

@client.command(name="음악", help="음악 관련 명령어를 확인합니다")
async def music_help(ctx):
    embed = discord.Embed(title="음악 명령어", description="음악 관련 명령어입니다.", color=0x00ff00)
    embed.add_field(name="*clear or cl", value="플레이리스트를 비웁니다. 사용법 : *clear", inline=False)
    embed.add_field(name="*pause or pa", value="현재 재생 중인 곡을 일시 중지합니다. 사용법 : *pause", inline=False)
    embed.add_field(name="*play or p [URL]", value="유튜브 URL을 플레이리스트에 추가합니다. 사용법 : *play [URL]", inline=False)
    embed.add_field(name="*playlist or pl", value="플레이리스트를 보여줍니다. 사용법 : *playlist", inline=False)
    embed.add_field(name="*resume or re", value="일시 중지된 곡을 다시 재생합니다. 사용법 : *resume", inline=False)
    embed.add_field(name="*search or s [검색어]", value="유튜브에서 검색한 후 선택할 수 있습니다. 사용법 : *search [검색어]", inline=False)
    embed.add_field(name="*skip or sk", value="현재 재생 중인 곡을 스킵합니다. 사용법 : *skip", inline=False)
    embed.add_field(name="*stop or st", value="재생을 중지하고 음성 채널에서 나갑니다. 사용법 : *stop", inline=False)
    embed.add_field(name="*volume or v", value="볼륨을 조절합니다. 사용법 : *volume [0~100]", inline=False)
    await ctx.send(embed=embed)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        ytdl.cookiefile = 'C:/Users/caos1/Desktop/개발/실험용 이것저것 봇/cookies.txt'  # 쿠키 파일 설정
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable=ffmpeg_path, **ffmpeg_options), data=data)

# 서버별 플레이리스트 설정
playlists = {}
# 서버별 음성 클라이언트 설정
voice_clients = {}
# 서버별 재생 상태 설정
is_playing = {}

async def search_youtube(query):
    query_string = quote(query)
    html = request.urlopen("https://www.youtube.com/results?search_query=" + query_string)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    unique_video_ids = list(dict.fromkeys(video_ids))  # 중복 제거
    return ["https://www.youtube.com/watch?v=" + video_id for video_id in unique_video_ids][:30]  # top 30 results

@client.command(name="search", aliases=['s'], hidden=True)
async def search(ctx, *, query):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    await ctx.send(f"검색 중입니다: {query}")
    try:
        search_results = await search_youtube(query)
        if not search_results:
            await ctx.send("검색 결과가 없습니다.")
            return

        items_per_page = 5
        pages = [search_results[i:i + items_per_page] for i in range(0, len(search_results), items_per_page)]
        current_page = 0

        def create_message(page):
            message = "검색 결과:\n"
            for idx, url in enumerate(page):
                message += f"{idx + 1}. {url}\n"
            message += f"Page {current_page + 1} of {len(pages)}"
            return message

        message = await ctx.send(create_message(pages[current_page]))
        emojis = ["⬅️", "➡️", "❌", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for emoji in emojis:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emojis

        while True:
            try:
                reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1
                    await message.edit(content=create_message(pages[current_page]))
                elif str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                    current_page += 1
                    await message.edit(content=create_message(pages[current_page]))
                elif str(reaction.emoji) == "❌":
                    await ctx.send("검색이 취소되었습니다.")
                    await message.delete()
                    return
                else:
                    index = emojis.index(str(reaction.emoji)) - 3
                    if 0 <= index < len(pages[current_page]):
                        url = pages[current_page][index]
                        await message.delete()  # 선택창 메시지 삭제
                        await play(ctx, url=url)
                        return
                await message.remove_reaction(reaction, ctx.author)
            except discord.Forbidden:
                await ctx.send("메시지 수정 권한이 없어 검색을 계속할 수 없습니다.")
                return
            except asyncio.TimeoutError:
                await ctx.send("검색 시간이 초과되었습니다.")
                await message.delete()
                return

    except Exception as e:
        await ctx.send(f"검색 중 오류가 발생했습니다: {str(e)}")

async def ensure_voice(ctx):
    if ctx.guild.id not in voice_clients or voice_clients[ctx.guild.id] is None:
        if ctx.author.voice:
            voice_clients[ctx.guild.id] = await ctx.author.voice.channel.connect()
        else:
            await ctx.send("음성 채널에 연결되어 있지 않습니다.")
            raise commands.CommandError("사용자가 음성 채널에 연결되어 있지 않습니다.")
    elif voice_clients[ctx.guild.id].channel != ctx.author.voice.channel:
        await voice_clients[ctx.guild.id].move_to(ctx.author.voice.channel)

@client.command(name="play", aliases=['p'], hidden=True)
async def play(ctx, *, url):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    await ensure_voice(ctx)

    # URL에서 제목 추출
    ytdl_opts_playlist = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'skip_download': True,
    }
    ytdl_playlist = youtube_dl.YoutubeDL(ytdl_opts_playlist)
    info = ytdl_playlist.extract_info(url, download=False)

    if 'entries' in info:
        for entry in info['entries']:
            if ctx.guild.id not in playlists:
                playlists[ctx.guild.id] = []
            playlists[ctx.guild.id].append({"url": entry['url'], "title": entry['title']})
            await ctx.send(f"{entry['title']}을(를) 플레이리스트에 추가했습니다.")
    else:
        title = info.get('title')
        if ctx.guild.id not in playlists:
            playlists[ctx.guild.id] = []
        playlists[ctx.guild.id].append({"url": url, "title": title})
        await ctx.send(f"{title}을(를) 플레이리스트에 추가했습니다.")

    # 현재 재생 중이 아니라면 재생 시작
    if ctx.guild.id not in is_playing or not is_playing[ctx.guild.id]:
        client.loop.create_task(play_next(ctx))

async def play_next(ctx):
    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
        return

    if ctx.guild.id in playlists and playlists[ctx.guild.id]:
        is_playing[ctx.guild.id] = True
        song = playlists[ctx.guild.id].pop(0)
        url = song["url"]
        title = song["title"]

        await ctx.send(f"[{title}]({url})을(를) 재생합니다.")
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
                voice_clients[ctx.guild.id].play(player, after=lambda e: client.loop.create_task(play_next(ctx)))
            except Exception as e:
                await ctx.send(f"재생할 수 없는 URL입니다: {str(e)}")
                is_playing[ctx.guild.id] = False
                client.loop.create_task(play_next(ctx))
    else:
        is_playing[ctx.guild.id] = False
        await voice_clients[ctx.guild.id].disconnect()
        voice_clients[ctx.guild.id] = None

@client.command(name="playlist", aliases=['pl'], hidden=True)
async def show_playlist(ctx):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.guild.id not in playlists or not playlists[ctx.guild.id]:
        await ctx.send("플레이리스트가 비어 있습니다.")
        return

    items_per_page = 10
    pages = [playlists[ctx.guild.id][i:i + items_per_page] for i in range(0, len(playlists[ctx.guild.id]), items_per_page)]
    current_page = 0

    def create_embed(page):
        embed = discord.Embed(title="플레이리스트", color=discord.Color.blue())
        for idx, song in enumerate(page):
            embed.add_field(name=f"{idx + 1}.", value=song["title"], inline=False)
        embed.set_footer(text=f"Page {current_page + 1} of {len(pages)}")
        return embed

    message = await ctx.send(embed=create_embed(pages[current_page]))
    emojis = ["⬅️", "➡️"]
    for emoji in emojis:
        await message.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in emojis

    while True:
        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=create_embed(pages[current_page]))
            elif str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(embed=create_embed(pages[current_page]))
            await message.remove_reaction(reaction, ctx.author)
        except asyncio.TimeoutError:
            break

@client.command(name="volume", aliases=['v'], hidden=True)
async def volume(ctx, volume: int):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.voice_client is None:
        return await ctx.send("음성 채널에 연결되어 있지 않습니다.")

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"볼륨이 {volume}%로 변경되었습니다.")

@client.command(name="stop", aliases=['st'], hidden=True)
async def stop(ctx):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.guild.id in is_playing:
        is_playing[ctx.guild.id] = False
    if ctx.guild.id in playlists:
        playlists.pop(ctx.guild.id)
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
        voice_clients[ctx.guild.id] = None

@client.command(name="clear", aliases=['cl'], hidden=True)
async def clear(ctx):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.guild.id in playlists:
        playlists.pop(ctx.guild.id)
    else:
        await ctx.send("플레이리스트가 비어 있습니다.")
    await ctx.send("플레이리스트를 비웠습니다.")

@client.command(name="pause", aliases=['pa'], hidden=True)
async def pause(ctx):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.voice_client.is_paused() or not ctx.voice_client.is_playing():
        await ctx.send("음악이 이미 일시 정지 중이거나 재생 중이지 않습니다.")
    else:
        await ctx.send("음악을 일시 정지합니다.")
        ctx.voice_client.pause()
        
@client.command(name="resume", aliases=['re'], hidden=True)
async def resume(ctx):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.voice_client.is_playing() or not ctx.voice_client.is_paused():
        await ctx.send("음악이 이미 재생 중이거나 재생할 음악이 존재하지 않습니다.")
    else:
        await ctx.send("음악을 다시 재생합니다.")  
        ctx.voice_client.resume()

@client.command(name="skip", aliases=['sk'], hidden=True)
async def skip(ctx):
    if ctx.author.voice is None:
        await ctx.send("음성 채널에 연결되어 있지 않습니다.")
        return

    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        await ctx.send("현재 재생 중인 곡이 없습니다.")
    else:
        ctx.voice_client.stop()
        await ctx.send("현재 곡을 건너뜁니다.")

#=======================================================================================================

@client.command(name='투자', help='투자 관련 명령어를 확인합니다.')  # 투자 관련 명령어
async def finance(ctx):
    embed = discord.Embed(title="투자 관련 명령어", description=f"투자 관련 명령어입니다.\n매수 매도에 시간이 조금 소요되니 양해바랍니다.", color=0xff0000)
    embed.add_field(name="계좌개설 or ma", value="계좌를 개설합니다.", inline=False)
    embed.add_field(name="주가 or price", value="*주가 [검색어]", inline=False)
    embed.add_field(name="네이버주가 or nav", value="*네이버주가 [검색어]", inline=False)
    embed.add_field(name="매수 or buy", value="*매수 [종목명] [수량]", inline=False)
    embed.add_field(name="매도 or sell", value="*매도 [종목명] [수량]", inline=False)
    embed.add_field(name="전량매도 or all", value="*전량매도 [종목명]", inline=False)
    embed.add_field(name="잔액", value="잔액을 확인합니다.", inline=False)
    embed.add_field(name="보유 or wallet", value="*보유 [필명(선택)]", inline=False)
    embed.add_field(name="포트폴리오 or port", value="*포트폴리오 [필명(선택)]", inline=False)
    embed.add_field(name="파산 or delete", value="계좌를 삭제합니다.", inline=False)
    embed.add_field(name="장시간 or market", value="장 시간을 확인합니다.", inline=False)
    embed.add_field(name="리더보드", value="리더보드를 확인합니다.", inline=False)
    embed.add_field(name="기록 or log", value="*기록 [필명(선택)]", inline=False)
    embed.add_field(name="송금 or transfer", value="*송금 [필명] [금액]", inline=False)

    await ctx.send(embed=embed)

def split_symbol(symbol_text):
    match = re.match(r'(\d+|[A-Za-z]+)(.*)', symbol_text)
    
    if match:
        stock_code = match.group(1)
        exchange = match.group(2).strip()
    else:
        stock_code = ''
        exchange = ''
    
    return stock_code, exchange


@client.command(name="네이버주가", aliases=['nav'], hidden=True)
async def 주가(ctx, query):
    try:
        global options

        url = 'https://www.naver.com/'
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        query = query + ' 주가'

        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "query"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        symbol_company = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main_pack"]/section[1]/div/div[2]/div[1]/div/h3/a/em'))
        )
        name = driver.find_element(By.XPATH, '//*[@id="main_pack"]/section[1]/div/div[2]/div[1]/div/h3/a/span[1]')
        current_price = driver.find_element(By.XPATH, '//*[@id="main_pack"]/section[1]/div/div[2]/div[1]/div/h3/a/span[2]/strong')
        change_rate = driver.find_element(By.XPATH, '//*[@id="main_pack"]/section[1]/div/div[2]/div[1]/div/h3/a/span[2]/span[2]/em[2]')
        change_price = driver.find_element(By.XPATH, '//*[@id="main_pack"]/section[1]/div/div[2]/div[1]/div/h3/a/span[2]/span[2]/em[1]')

        symbol, exchange = split_symbol(symbol_company.text)

        if "-" in change_rate.text:
            color = 0x0000FF
            change_price_value = change_price.text
        else:
            color = 0xFF0000
            change_price_value = "+" + change_price.text

        embed = discord.Embed(title=f'{name.text}({symbol})', color=color)
        embed.add_field(name='현재가', value=current_price.text, inline=False)
        embed.add_field(name='변동률', value=change_rate.text, inline=False)
        embed.add_field(name='변동가', value=change_price_value, inline=False)
        embed.set_footer(text=exchange)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send('죄송합니다. 자세한 정보는 네이버 증권을 이용해주세요.')
        print(f"Error: {e}")
    finally:
        driver.quit()

@client.command(name='입금', aliases=['deposit'], hidden=True)
async def add_balance(ctx, nickname: str, amount: int):
    if str(ctx.author.id) not in ALLOWED_USERS:
        await ctx.send('이 명령어를 사용할 권한이 없습니다.')
        return

    # 필명에 해당하는 사용자를 찾습니다.
    user_id = None
    for account_id, account_info in accounts.items():
        if account_info['nickname'] == nickname:
            user_id = account_id
            break

    if not user_id:
        await ctx.send(f'{nickname}이라는 필명을 가진 사용자를 찾을 수 없습니다.')
        return

    accounts[user_id]['balance'] += amount
    with open(stock_txt, 'w') as file:
        json.dump(accounts, file)
    await ctx.send(f'{amount:,.0f}원이 {nickname}의 계좌에 추가되었습니다. 현재 잔액: {accounts[user_id]["balance"]:,.0f}원')

@client.command(name='출금', aliases=['withdraw'], hidden=True)
async def subtract_balance(ctx, nickname: str, amount: int):
    if str(ctx.author.id) not in ALLOWED_USERS:
        await ctx.send('이 명령어를 사용할 권한이 없습니다.')
        return
    
    # 필명에 해당하는 사용자를 찾습니다.
    user_id = None
    for account_id, account_info in accounts.items():
        if account_info['nickname'] == nickname:
            user_id = account_id
            break
    if not user_id:
        await ctx.send(f'{nickname}이라는 필명을 가진 사용자를 찾을 수 없습니다.')
        return
    
    accounts[user_id]['balance'] -= amount
    with open(stock_txt, 'w') as file:
        json.dump(accounts, file)
    await ctx.send(f'{amount:,.0f}원이 {nickname}의 계좌에서 출금되었습니다. 현재 잔액: {accounts[user_id]["balance"]:,.0f}원')

@client.command(name='송금', aliases=['transfer'], hidden=True)
async def transfer_balance(ctx, amount: int, receiver_nickname: str):
    sender_id = str(ctx.author.id)

    if sender_id not in accounts:
        await ctx.send('먼저 계좌를 개설해주세요.')
        return

    sender_nickname = accounts[sender_id]['nickname']

    # 수신자 필명에 해당하는 사용자를 찾습니다.
    receiver_id = None
    for account_id, account_info in accounts.items():
        if account_info['nickname'] == receiver_nickname:
            receiver_id = account_id
            break
    if not receiver_id:
        await ctx.send(f'{receiver_nickname}이라는 필명을 가진 사용자를 찾을 수 없습니다.')
        return

    if accounts[sender_id]['balance'] < amount:
        await ctx.send('잔액이 부족합니다.')
        return

    accounts[sender_id]['balance'] -= amount
    accounts[receiver_id]['balance'] += amount
    with open(stock_txt, 'w') as file:
        json.dump(accounts, file)
    await ctx.send(f'{sender_nickname}님의 계좌에서 {receiver_nickname}님의 계좌로 {amount:,.0f}원이 송금되었습니다.')

accounts = {}
if os.path.exists(stock_txt) and os.path.getsize(stock_txt) > 0:
    with open(stock_txt, 'r') as file:
        accounts = json.load(file)

start_balance = 50000000

@client.command(name='계좌개설', aliases=['ma'], hidden=True)
async def open_account(ctx):
    dm_channel = await ctx.author.create_dm()

    if str(ctx.author.id) in accounts:
        await dm_channel.send('이미 계좌가 있습니다!')
    else:
        await dm_channel.send('필명을 입력해주세요 (취소하려면 "취소"를 입력하세요):')
        def check(msg):
            return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)
        while True:
            msg = await client.wait_for('message', check=check)
            nickname = msg.content
            if nickname == "취소":
                await dm_channel.send('계좌 개설이 취소되었습니다.')
                break
            elif any(account['nickname'] == nickname for account in accounts.values()):
                await dm_channel.send('이미 사용 중인 필명입니다. 다른 필명을 입력해주세요.')
            else:
                accounts[str(ctx.author.id)] = {'nickname': nickname, 'balance': start_balance, 'portfolio': {}}
                with open(stock_txt, 'w') as file:
                    json.dump(accounts, file)
                await dm_channel.send(f'{nickname} 계좌가 개설되었습니다. 초기 잔액: 5,000만원')
                break

@client.command(name='리더보드', aliases=['leaderboard'], hidden=True)
async def leaderboard(ctx):
    leaderboard_data = []

    for user_id, account in accounts.items():
        total_balance = account['balance']
        for name, info in account['portfolio'].items():
            current_price, _, _, _, _ = await get_stock_price(name)
            if current_price:
                total_balance += current_price * info['quantity']
            else:
                total_balance += info['total_amount']  # If current price is not available, use the total amount spent

        leaderboard_data.append((account['nickname'], total_balance))

    leaderboard_data.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title="리더보드", description="유저 순위와 총 자산", color=0x00ff00)
    for idx, (nickname, total_balance) in enumerate(leaderboard_data, start=1):
        embed.add_field(name=f"{idx}위: {nickname}", value=f"총 자산: {total_balance:,.0f}원", inline=False)

    await ctx.send(embed=embed)

def classify_data(data):
    if data.isdigit():
        return "국내"
    elif data.isalpha() and data.isascii():
        return "미국"
    else:
        return None

async def get_stock_price(query):
    if not query:
        print("Error: query가 없습니다.")
        return None, None, None, "Wrong query", None

    driver = None
    try:
        global options

        # 크롬드라이버로 원하는 url로 접속
        url = 'https://www.tossinvest.com/'
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        await asyncio.sleep(2)

        # 검색창에 키워드 입력 후 엔터
        search_box1 = driver.find_element(By.XPATH, '//*[@id="tossinvest_global_navigation_bar"]/nav/div[2]/div/button')
        search_box1.click()
        await asyncio.sleep(2)

        search_box2 = driver.find_element(By.XPATH, '//*[@id="radix-:R9alb6m6:"]/div[1]/input')
        search_box2.send_keys(query)
        search_box2.send_keys(Keys.RETURN)
        await asyncio.sleep(2)

        symbol = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[1]/span[2]')

        country = classify_data(symbol.text)

        if "국내" in country:
            name = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[1]/span[1]')
            current_price = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[2]/span[1]/span')
            change_rate_price = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[2]/span[3]/span')
        elif "미국" in country:
            name = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[1]/span[1]')
            current_price = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[2]/span[1]/span')
            change_rate_price = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div/div[3]/div/div[3]/div[2]/span[4]/span')
        else:
            return None, None, None, None, None

        current_price_text = current_price.text.replace(',', '').replace('원', '')
        change_rate_price_text = change_rate_price.text.replace(',', '').replace('원', '')

        return float(current_price_text), change_rate_price_text, symbol.text, name.text, country

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None, None, None

    finally:
        if driver:
            driver.quit()

@client.command(name="주가", aliases=['price'], hidden=True)
async def 토스주가(ctx, query):
    # 안내 메시지를 보냅니다.
    notification_message = await ctx.send('주가를 확인하는 중입니다....')

    current_price, change_rate_price, symbol, name, country = await get_stock_price(query)

    if name is None:
        await ctx.send('죄송합니다. 자세한 정보는 토스 증권을 이용해주세요.')
        return
    
    # await notification_message.delete()  # This line is removed to prevent double deletion

    if "-" in change_rate_price:
        color = 0x0000FF
        change_price_value = change_rate_price
    else:
        color = 0xFF0000
        change_price_value = change_rate_price

    await notification_message.delete()

    if current_price:
        embed = discord.Embed(title=f'{name}({symbol})', description=f"기준시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", color=color)    
        embed.add_field(name='현재가', value=f"{current_price:,.0f}원", inline=False)
        embed.add_field(name='변동', value=f"{change_price_value}", inline=False)
        embed.set_footer(text=f'토스 증권 / {country}장')
        await ctx.send(embed=embed)
    else:
        await ctx.send('죄송합니다. 자세한 정보는 토스 증권을 이용해주세요.')

@client.command(name='장시간', aliases=['market'], hidden=True)
async def market(ctx):
    embed = discord.Embed(title="장 시간", description="한국 기준 장 시간을 확인합니다.", color=0x00ff00)
    embed.add_field(name="국내장 시작", value="오전 9시", inline=True)
    embed.add_field(name="국내장 종료", value="오후 3시 30분", inline=False)
    embed.add_field(name="-------------------------", value="\u200b", inline=False)
    embed.add_field(name="미국 데이마켓", value="오전 10시 ~ 오후 5시 30분", inline=False)
    embed.add_field(name="미국 프리마켓", value="오후 6시 ~ 오후 11시 30분", inline=False)
    embed.add_field(name="미국장 시작", value="오후 10시 30분", inline=True)
    embed.add_field(name="미국장 종료", value="오전 4시", inline=False)
    embed.add_field(name="미국 에프터마켓", value="오전 6시 ~ 오전 8시", inline=False)

    await ctx.send(embed=embed)

def log_transaction(nickname, action, stock_name, quantity, price, total_amount):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()} - {nickname} - {action} - {stock_name} - {quantity}주 - {price}원 - {total_amount}원\n")

@client.command(name='매수', aliases=['buy'], hidden=True)
async def buy(ctx, query: str = None, quantity: float = None):
    if str(ctx.author.id) not in accounts:
        await ctx.send('먼저 계좌를 개설해주세요.')
        return
    if quantity is None:
        await ctx.send('매수할 수량을 입력해주세요!')
        return
    if query is None:
        await ctx.send('매수할 종목을 입력해주세요!')
        return

    notification_message = await ctx.send('매수를 진행합니다...')
    current_price, _, _, name, country = await get_stock_price(query)

    now = datetime.datetime.now()

    if country == "국내":
        if now.weekday() >= 5 or now.hour < 9 or (now.hour == 15 and now.minute > 30) or now.hour > 15:
            await notification_message.delete()
            await ctx.send('국내장은 오전 9시부터 오후 3시 30분까지입니다.')
            return
    elif country == "미국":
        if now.weekday() >= 5 or (now.hour < 10 and now.hour >= 8) or (now.hour >= 17.5 and now.hour < 18):
            await notification_message.delete()
            await ctx.send(f'미국장은 \n데이마켓: 오전 10시 ~ 오후 5시 30분\n프리마켓: 오후 6시 ~ 오후 11시 30분\n본장: 오후 11시 30분 ~ 오전 6시\n에프터마켓: 오전 6시 ~ 오전 8시\n입니다. 투자에 참고 바랍니다.')
            return
        
    if not current_price:
        await notification_message.delete()
        await ctx.send('죄송합니다. 주식 정보를 가져올 수 없습니다.')
        return

    total_amount = current_price * quantity
    if accounts[str(ctx.author.id)]['balance'] < total_amount:
        await notification_message.delete()
        await ctx.send('잔액이 부족합니다.')
    else:
        accounts[str(ctx.author.id)]['balance'] -= total_amount
        if name in accounts[str(ctx.author.id)]['portfolio']:
            accounts[str(ctx.author.id)]['portfolio'][name]['quantity'] += quantity
            accounts[str(ctx.author.id)]['portfolio'][name]['total_amount'] += total_amount
        else:
            accounts[str(ctx.author.id)]['portfolio'][name] = {'quantity': quantity, 'total_amount': total_amount}
        
        with open(stock_txt, 'w') as file:
            json.dump(accounts, file)
        
        log_transaction(accounts[str(ctx.author.id)]['nickname'], '매수', name, quantity, current_price, total_amount)

        await notification_message.delete()
        await ctx.send(f'{name} {quantity}주 매수 완료. 현재 잔액: {accounts[str(ctx.author.id)]["balance"]:,.0f}원 \n매수가: {current_price:,.0f}원, 총액: {total_amount:,.0f}원')

@client.command(name='매도', aliases=['sell'], hidden=True)
async def sell(ctx, query: str = None, quantity: float = None):
    if str(ctx.author.id) not in accounts:
        await ctx.send('먼저 계좌를 개설해주세요.')
        return
    if quantity is None:
        await ctx.send('매도할 수량을 입력해주세요!')
        return
    if query is None:
        await ctx.send('매도할 종목을 입력해주세요!')
        return
    
    notification_message = await ctx.send('매도를 진행합니다...')    
    current_price, _, _, name, country = await get_stock_price(query)
    if not name in accounts[str(ctx.author.id)]['portfolio']:
        await notification_message.delete()
        await ctx.send('보유한 종목이 아닙니다.')
        return
    if not current_price:
        await notification_message.delete()
        await ctx.send('죄송합니다. 주식 정보를 가져올 수 없습니다.')
        return

    now = datetime.datetime.now()

    if country == "국내":
        if now.weekday() >= 5 or now.hour < 9 or (now.hour == 15 and now.minute > 30) or now.hour > 15:
            await notification_message.delete()
            await ctx.send('국내장은 오전 9시부터 오후 3시 30분까지입니다.')
            return
    elif country == "미국":
        if now.weekday() >= 5 or (now.hour < 10 and now.hour >= 8) or (now.hour >= 17.5 and now.hour < 18):
            await notification_message.delete()
            await ctx.send(f'미국장은 \n데이마켓: 오전 10시 ~ 오후 5시 30분\n프리마켓: 오후 6시 ~ 오후 11시 30분\n본장: 오후 11시 30분 ~ 오전 6시\n에프터마켓: 오전 6시 ~ 오전 8시\n입니다. 투자에 참고 바랍니다.')
            return
        
    if name not in accounts[str(ctx.author.id)]['portfolio'] or accounts[str(ctx.author.id)]['portfolio'][name]['quantity'] < quantity:
        await ctx.send('보유한 수량이 부족합니다.')
        return

    total_amount = current_price * quantity
    average_price = accounts[str(ctx.author.id)]['portfolio'][name]['total_amount'] / accounts[str(ctx.author.id)]['portfolio'][name]['quantity']
    profit_loss = (current_price - average_price) * quantity
    profit_loss_percent = (current_price - average_price) / average_price * 100

    accounts[str(ctx.author.id)]['balance'] += total_amount
    accounts[str(ctx.author.id)]['portfolio'][name]['quantity'] -= quantity
    accounts[str(ctx.author.id)]['portfolio'][name]['total_amount'] -= total_amount
    if accounts[str(ctx.author.id)]['portfolio'][name]['quantity'] == 0:
        del accounts[str(ctx.author.id)]['portfolio'][name]

    with open(stock_txt, 'w') as file:
        json.dump(accounts, file)
    
    log_transaction(accounts[str(ctx.author.id)]['nickname'], '매도', name, quantity, current_price, total_amount)

    await notification_message.delete()
    await ctx.send(f'{name} {quantity}주 매도 완료. 현재 잔액: {accounts[str(ctx.author.id)]["balance"]:,.0f}원\n매도가: {current_price:,.0f}원, 손익: {profit_loss:,.0f}원 ({profit_loss_percent:.2f}%)')

@client.command(name='전량매도', aliases=['all'], hidden=True) #보유한 모든 주식을 전부 팔기
async def sell_all(ctx):
    if str(ctx.author.id) not in accounts:
        await ctx.send('먼저 계좌를 개설해주세요.')
        return
    
    notification_message = await ctx.send('보유한 모든 주식을 전량 매도합니다. 종목이 많을수록 오래걸립니다..')
    items_to_sell = list(accounts[str(ctx.author.id)]['portfolio'].items())

    for name, info in items_to_sell:
        current_price, _, _, _, country = await get_stock_price(name)

        now = datetime.datetime.now()

        if not current_price:
            await notification_message.delete()
            await ctx.send('죄송합니다. 주식 정보를 가져올 수 없습니다.')
            return
        if country == "국내":
            if now.weekday() >= 5 or now.hour < 9 or (now.hour == 15 and now.minute > 30) or now.hour > 15:
                await notification_message.delete()
                await ctx.send('국내장은 오전 9시부터 오후 3시 30분까지입니다.')
                return
        elif country == "미국":
            if now.weekday() >= 5 or (now.hour < 10 and now.hour >= 8) or (now.hour >= 17.5 and now.hour < 18):
                await notification_message.delete()
                await ctx.send(f'미국장은 \n데이마켓: 오전 10시 ~ 오후 5시 30분\n프리마켓: 오후 6시 ~ 오후 11시 30분\n본장: 오후 11시 30분 ~ 오전 6시\n에프터마켓: 오전 6시 ~ 오전 8시\n입니다. 투자에 참고 바랍니다.')
                return
        
        quantity = info['quantity']
        total_amount = current_price * quantity

        accounts[str(ctx.author.id)]['balance'] += total_amount
        accounts[str(ctx.author.id)]['portfolio'][name]['quantity'] -= quantity
        accounts[str(ctx.author.id)]['portfolio'][name]['total_amount'] -= total_amount
        if accounts[str(ctx.author.id)]['portfolio'][name]['quantity'] == 0:
            del accounts[str(ctx.author.id)]['portfolio'][name]

        log_transaction(accounts[str(ctx.author.id)]['nickname'], '전량매도', name, quantity, current_price, total_amount)

    with open(stock_txt, 'w') as file:
        json.dump(accounts, file)

    await notification_message.delete()
    await ctx.send(f'보유한 모든 주식을 전량 매도 완료. 현재 잔액: {accounts[str(ctx.author.id)]["balance"]:,.0f}원')
        

@client.command(name='기록', aliases=['log'], hidden=True)
async def show_log(ctx, nickname: str = None):
    if nickname:
        user_id = None
        for account_id, account_info in accounts.items():
            if account_info['nickname'] == nickname:
                user_id = account_id
                break
        if not user_id:
            await ctx.send('해당 사용자가 없습니다.')
            return
    else:
        user_id = str(ctx.author.id)

    if user_id not in accounts:
        await ctx.send('먼저 계좌를 개설해주세요.')
        return

    with open(log_file, 'r', encoding='utf-8') as f:
        logs = [line.strip() for line in f if line.split(' - ')[1] == accounts[user_id]['nickname']]

    if not logs:
        await ctx.send('거래 내역이 없습니다.')
        return

    items_per_page = 5
    pages = [logs[i:i + items_per_page] for i in range(0, len(logs), items_per_page)]
    current_page = 0

    def create_embed(page):
        embed = discord.Embed(title=f"{accounts[user_id]['nickname']}님의 거래 내역", color=0x00FF00)
        for log in page:
            embed.add_field(name='\u200b', value=log, inline=False)
        embed.set_footer(text=f"Page {current_page + 1} of {len(pages)}")
        return embed

    message = await ctx.send(embed=create_embed(pages[current_page]))
    emojis = ["⬅️", "➡️"]
    for emoji in emojis:
        await message.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in emojis

    while True:
        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=create_embed(pages[current_page]))
            elif str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(embed=create_embed(pages[current_page]))
            await message.remove_reaction(reaction, ctx.author)
        except asyncio.TimeoutError:
            break

@client.command(name='잔액', hidden=True)
async def portfolio(ctx):
    if str(ctx.author.id) not in accounts:
        await ctx.send('먼저 계좌를 개설해주세요.')
        return
    
    await ctx.send(f'현재 잔액: {accounts[str(ctx.author.id)]["balance"]:,.0f}원')

@client.command(name='보유', aliases=['wallet'], hidden=True)
async def wallet(ctx, nickname: str = None):
    dm_channel = await ctx.author.create_dm()

    if nickname:
        user_id = None
        for account_id, account_info in accounts.items():
            if account_info['nickname'] == nickname:
                user_id = account_id
                break
        if not user_id:
            await ctx.send('해당 사용자가 없습니다.')
            return
    else:
        user_id = str(ctx.author.id)

    if user_id not in accounts:
        await dm_channel.send('먼저 계좌를 개설해주세요.')
        return

    # 안내 메시지를 보냅니다.
    notification_message = await ctx.send('보유 목록을 확인합니다..')
    account = accounts[user_id]
    total_balance = account['balance']
    embed_pages = []
    current_page = 0

    embed = discord.Embed(title=f"{account['nickname']}님의 보유 자산", color=0x00FF00)
    embed.add_field(name='잔액', value=f"{account['balance']:,.0f}원", inline=False)

    for name, info in account['portfolio'].items():
        quantity = info['quantity']
        average_price = info['total_amount'] / info['quantity']
        total_average_balance = info['total_amount']
        total_balance += total_average_balance
        embed.add_field(name=f"{name}", value=f"수량: {quantity:,.0f}주, 1주 평균: {average_price:,.0f}원\n구매: {total_average_balance:,.0f}원\n", inline=False)

        if len(embed.fields) >= 5:
            embed_pages.append(embed)
            embed = discord.Embed(title=f"{account['nickname']}님의 보유 자산", color=0x00FF00)

    await notification_message.delete()
    embed_pages.append(embed)

    for embed in embed_pages:
        if total_balance >= start_balance:
            embed.color = 0xFF0000
        else:
            embed.color = 0x0000FF

    profit = total_balance - start_balance
    profit_percent = profit / start_balance * 100
    embed_pages[-1].add_field(name='총 자산', value=f"{total_balance:,.0f}원, 손익: {profit:,.0f}원({profit_percent:.2f}%)", inline=False)

    message = await ctx.send(embed=embed_pages[0])

    for i, embed in enumerate(embed_pages):
        embed.set_footer(text=f"Page {i + 1} of {len(embed_pages)}")

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

    while True:
        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=embed_pages[current_page])
            elif str(reaction.emoji) == "➡️" and current_page < len(embed_pages) - 1:
                current_page += 1
                await message.edit(embed=embed_pages[current_page])
            await message.remove_reaction(reaction, ctx.author)
        except asyncio.TimeoutError:
            break

@client.command(name='포트폴리오', aliases=['port'], hidden=True)
async def portfolio(ctx, nickname: str = None):
    start_time = time.time()  # 시작 시간 기록
    dm_channel = await ctx.author.create_dm()

    if nickname:
        user_id = None
        for account_id, account_info in accounts.items():
            if account_info['nickname'] == nickname:
                user_id = account_id
                break
        if not user_id:
            await ctx.send('해당 사용자가 없습니다.')
            return
    else:
        user_id = str(ctx.author.id)

    if user_id not in accounts:
        await dm_channel.send('먼저 계좌를 개설해주세요.')
        return

    # 안내 메시지를 보냅니다.
    notification_message = await ctx.send('포트폴리오를 확인합니다. 종목이 많을수록 오래걸립니다...')

    account = accounts[user_id]
    total_balance = account['balance']
    embed_pages = []
    current_page = 0
    quantity = 0

    embed = discord.Embed(title=f"{account['nickname']}님의 포트폴리오", description=f"기준시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", color=0x00FF00)
    embed.add_field(name='잔액', value=f"{account['balance']:,.0f}원", inline=False)

    for name, info in account['portfolio'].items():
        current_price, _, symbol, _, _ = await get_stock_price(name)
        if current_price:
            quantity = info['quantity']
            current_price_value = current_price
            average_price = info['total_amount'] / info['quantity']
            total_average_balance = info['total_amount']
            total_current_balance = current_price * info['quantity']
            profit_loss = current_price * info['quantity'] - info['total_amount']
            profit_loss_percent = (current_price - average_price) / average_price * 100
            total_balance += info['quantity'] * current_price
            embed.add_field(name=f"{name} ({symbol})", value=f"수량: {quantity:,.0f}주, 1주 평균: {average_price:,.0f}원, 1주: {current_price_value:,.0f}원\n구매: {total_average_balance:,.0f}원, 현재: {total_current_balance:,.0f}원\n손익: {profit_loss_percent:.2f}%, 손익가: {profit_loss:,.0f}원", inline=False)
        else:
            average_price = info['total_amount'] / info['quantity']
            total_balance += info['total_amount']
            embed.add_field(name=f"{name} ({symbol})", value=f"수량: {quantity:,.0f}주, 평단가: {average_price:,.0f}원, 현재가: 주식 정보를 가져올 수 없음", inline=False)

        if len(embed.fields) >= 5:
            embed_pages.append(embed)
            embed = discord.Embed(title=f"{account['nickname']}님의 포트폴리오", description=f"기준시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", color=0x00FF00)

    await notification_message.delete()
    embed_pages.append(embed)

    for embed in embed_pages:
        if total_balance >= start_balance:
            embed.color = 0xFF0000
        else:
            embed.color = 0x0000FF

    profit = total_balance - start_balance
    profit_percent = profit / start_balance * 100
    
    embed_pages[0].add_field(name='총 자산', value=f"{total_balance:,.0f}원, 손익: {profit:,.0f}원({profit_percent:.2f}%)", inline=False)

    message = await ctx.send(embed=embed_pages[0])
    end_time = time.time()  # 종료 시간 기록
    elapsed_time = end_time - start_time  # 경과 시간 계산
    await ctx.send(f"출력 소요 시간: {elapsed_time:.2f}초")

    for i, embed in enumerate(embed_pages):
        embed.set_footer(text=f"Page {i + 1} of {len(embed_pages)}")

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

    while True:
        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=embed_pages[current_page])
            elif str(reaction.emoji) == "➡️" and current_page < len(embed_pages) - 1:
                current_page += 1
                await message.edit(embed=embed_pages[current_page])
            await message.remove_reaction(reaction, ctx.author)
        except asyncio.TimeoutError:
            break

    
@client.command(name='내종목', aliases=['profit'], hidden=True)
async def profit(ctx, stock_name: str = None):
    dm_channel = await ctx.author.create_dm()
    user_id = str(ctx.author.id)

    if user_id not in accounts:
        await dm_channel.send('먼저 계좌를 개설해주세요.')
        return
    
    notification_message = await ctx.send(f'{accounts[user_id]["nickname"]}님의 {stock_name}의 현재가를 확인합니다...')
    current_price, _, symbol, name, _ = await get_stock_price(stock_name)
    if not current_price:
        await notification_message.delete()
        await ctx.send('죄송합니다. 주식 정보를 가져올 수 없습니다.')
        return
    
    account = accounts[user_id]
    if name not in account['portfolio']:
        await notification_message.delete()
        await ctx.send('보유한 종목이 아닙니다.')
        return
    
    info = account['portfolio'][name]
    quantity = info['quantity']
    average_price = info['total_amount'] / info['quantity']
    total_average_balance = info['total_amount']
    total_current_balance = current_price * info['quantity']
    profit_loss = current_price * info['quantity'] - info['total_amount']
    profit_loss_percent = (current_price - average_price) / average_price * 100

    embed = discord.Embed(title=f"{account['nickname']}님의 {name}종목 손익", color=0x00FF00)
    embed.add_field(name=f"{name} ({symbol})", value=f"수량: {quantity:,.0f}주, 1주 평균: {average_price:,.0f}원, 1주: {current_price:,.0f}원\n구매: {total_average_balance:,.0f}원, 현재: {total_current_balance:,.0f}원\n손익: {profit_loss_percent:.2f}%, 손익가: {profit_loss:,.0f}원", inline=False)

    await notification_message.delete()
    await ctx.send(embed=embed)
    
@client.command(name='파산', aliases=['delete'], hidden=True)
async def bankrupt(ctx):
    dm_channel = await ctx.author.create_dm()
    if str(ctx.author.id) not in accounts:
        await dm_channel.send('먼저 계좌를 개설해주세요.')
        return

    await dm_channel.send('정말 파산하시겠습니까? 필명을 입력해주세요 (취소하려면 "취소"를 입력하세요):')
    def check(msg):
        return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)
    msg = await client.wait_for('message', check=check)
    if msg.content == "취소":
        await dm_channel.send('계좌 삭제가 취소되었습니다.')
    elif msg.content == accounts[str(ctx.author.id)]['nickname']:
        nickname = accounts[str(ctx.author.id)]['nickname']
        del accounts[str(ctx.author.id)]
        with open(stock_txt, 'w') as file:
            json.dump(accounts, file)
        
        # 거래 기록 삭제
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
        with open(log_file, 'w', encoding='utf-8') as f:
            for log in logs:
                if nickname not in log:
                    f.write(log)
        
        await dm_channel.send(f'계좌와 거래 기록이 삭제되었습니다.\n그동안 이용해주셔서 감사합니다! \n{ctx.author.mention}님! \n다시 계좌를 개설하려면 *계좌개설 명령어를 사용해주세요.')
    else:
        await dm_channel.send('필명이 일치하지 않습니다. 계좌 삭제가 취소되었습니다.')

#=======================================================================================================

gambling_accounts = {}
gambling_start_balance = 10000
if os.path.exists(gambling_txt) and os.path.getsize(gambling_txt) > 0:
    with open(gambling_txt, 'r') as file:
        gambling_accounts = json.load(file)

@client.command(name='도박', aliases=['gambling'], hidden=True)
async def gambling_help(ctx):
    embed = discord.Embed(title="도박 도움말", color=0x00ff00)
    embed.add_field(name="도박계좌개설 or ga_ma", value="도박 계좌를 개설합니다.", inline=False)
    embed.add_field(name="도박잔액 or ga_ba", value="도박 계좌의 잔액을 확인합니다.", inline=False)
    embed.add_field(name="배팅 or ga_b [금액]", value="배팅을 진행합니다.", inline=False)
    embed.add_field(name="구제 or ga_r", value="구제금액을 받습니다.", inline=False)
    embed.add_field(name="도박순위 or ga_rk", value="도박 순위를 확인합니다.", inline=False)
    await ctx.send(embed=embed)

@client.command(name='도박계좌개설', aliases=['ga_ma'], hidden=True)
async def open_gambling_account(ctx):
    dm_channel = await ctx.author.create_dm()

    if str(ctx.author.id) in gambling_accounts:
        await dm_channel.send('이미 계좌가 있습니다!')
    else:
        await dm_channel.send('필명을 입력해주세요 (취소하려면 "취소"를 입력하세요):')
        def check(msg):
            return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)
        while True:
            msg = await client.wait_for('message', check=check)
            nickname = msg.content
            if nickname == "취소":
                await dm_channel.send('계좌 개설이 취소되었습니다.')
                break
            elif any(account['nickname'] == nickname for account in gambling_accounts.values()):
                await dm_channel.send('이미 사용 중인 필명입니다. 다른 필명을 입력해주세요.')
            else:
                gambling_accounts[str(ctx.author.id)] = {'nickname': nickname, 'balance': gambling_start_balance}
                with open(gambling_txt, 'w') as file:
                    json.dump(gambling_accounts, file)
                await dm_channel.send(f'{nickname} 계좌가 개설되었습니다. 초기 잔액: 1만원')
                break

@client.command(name='도박잔액', aliases=['ga_ba'], hidden=True)
async def check_gambling_balance(ctx):
    if str(ctx.author.id) in gambling_accounts:
        balance = gambling_accounts[str(ctx.author.id)]['balance']
        nickname = gambling_accounts[str(ctx.author.id)]['nickname']
        await ctx.send(f'{nickname}님의 잔액은 {balance:,.0f}원입니다.')
    else:
        await ctx.send(f'{ctx.author.mention}님은 계좌를 개설하지 않았습니다.')

@client.command(name='배팅', aliases=['ga_b'], hidden=True)
async def bet(ctx, amount: int = None):
    if str(ctx.author.id) in gambling_accounts:
        if amount is None:
            await ctx.send('배팅 금액을 입력해주세요.')
        elif amount <= 0:
            await ctx.send('배팅 금액은 0보다 커야 합니다.')
        elif amount > gambling_accounts[str(ctx.author.id)]['balance']:
            await ctx.send('잔액이 부족합니다.')
        else:
            gambling_accounts[str(ctx.author.id)]['balance'] -= amount
            with open(gambling_txt, 'w') as file:
                json.dump(gambling_accounts, file)
            nickname = gambling_accounts[str(ctx.author.id)]['nickname']
            await ctx.send(f'{nickname}님의 배팅 금액은 {amount:,.0f}원입니다.')
            
            await asyncio.sleep(1)
            notification_message = await ctx.send('결과를 기다리는 중...')
            result = random.choice(['win', 'lose'])
            if result == 'win':
                gambling_accounts[str(ctx.author.id)]['balance'] += amount * 2
                await ctx.send(f'{nickname}님은 배팅에 성공하여 {amount * 2:,.0f}원을 획득했습니다.')
            else:
                await ctx.send(f'{nickname}님은 배팅에 실패하여 {amount:,.0f}원을 잃었습니다.')
                with open(gambling_txt, 'w') as file:
                    json.dump(gambling_accounts, file)
            await notification_message.delete()
    else:
        await ctx.send(f'{ctx.author.mention}님은 계좌를 개설하지 않았습니다.')

@client.command(name='구제', aliases=['ga_r'], hidden=True)
async def rescue(ctx):
    if str(ctx.author.id) in gambling_accounts:
        if gambling_accounts[str(ctx.author.id)]['balance'] == 0:
            gambling_accounts[str(ctx.author.id)]['balance'] += gambling_start_balance
            with open(gambling_txt, 'w') as file:
                json.dump(gambling_accounts, file)
            nickname = gambling_accounts[str(ctx.author.id)]['nickname']
            await ctx.send(f'{nickname}님은 구제금액 {gambling_start_balance:,.0f}원을 받았습니다.')
        else:
            await ctx.send('구제를 받을 수 있는 상태가 아닙니다.')
            
    else:
        await ctx.send(f'{ctx.author.mention}님은 계좌를 개설하지 않았습니다.')

@client.command(name='도박순위', aliases=['ga_rk'], hidden=True)
async def gambling_rank(ctx):
    sorted_accounts = sorted(gambling_accounts.items(), key=lambda x: x[1]['balance'], reverse=True)
    embed = discord.Embed(title="도박 순위", color=0xffffff)
    for i, (user_id, account) in enumerate(sorted_accounts):
        embed.add_field(name=f'{i + 1}위 {account["nickname"]}', value=f'{account["balance"]:,.0f}원', inline=False)
    await ctx.send(embed=embed)

#=======================================================================================================

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")
    elif isinstance(error, AttributeError) and 'NoneType' in str(error):
        await ctx.send("오류 발생: 음성 채널에 연결되어 있지 않습니다.")
    elif isinstance(error, discord.NotFound):
        return
    else:
        await ctx.send(f"오류 발생: {str(error)}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    ctx = await client.get_context(message)
    if ctx.command and ctx.command.name in restricted_commands:
        await ctx.send(f'{ctx.command.name} 명령어는 현재 제한되어 있습니다.')
        return

    await client.process_commands(message)

#=======================================================================================================

async def main():
    async with client:
        await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())
