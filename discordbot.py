import discord, openai, os, time, random, asyncio, requests, datetime
from discord.ext import commands
from cmath import log
from distutils.sysconfig import PREFIX
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
client = commands.Bot(command_prefix='*')

openai.api_key = "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"
riot_api_key = "RGAPI-a217785d-eacb-46d7-a01e-e21635982341"

#=============================================================

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

@client.event
async def on_ready():
    print('Bot is ready.')

    
#==============================================================

@client.command(name='안녕', aliases=['안녕하세요', 'ㅎㅇ', '하이'], help='인사해봅시다!')
async def hello(ctx):
    await ctx.send(f"{ctx.author} | {ctx.author.mention}, 안녕하세요!")

#==============================================================
@client.command(name='질문', aliases=['선생님'], help='Open AI 의 답변을 가져옵니다.')
async def ask_gpt(ctx, *, question):
    #message =  await ctx.send("만약, 답답하다고 느껴지시면\n https://chat.openai.com/ \n이 사이트를 방문하시길 바랍니다. \n답변을 작성중이니 조금 기다려주시길 바랍니다.")
    # 메시지 ID를 변수에 저장
    #message_id = message.id
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": question}
        ]
    )
    answer = result['choices'][0]['message']['content']
    #await ctx.channel.fetch_message(message_id).delete()
    await ctx.send(f"{ctx.author.mention}님, 제가 생각하는 답변은 다음과 같습니다.\n {answer}")
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

#챔피언 이름 들고오는 함수
def get_champion_name(champion_id):
    response = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{get_version()}/data/ko_KR/champion.json")
    response_json = response.json()
    champion_name = response_json['data'][champion_id]['name']
    return champion_name

# 소환사명으로부터 puuid를 가져오는 함수
def get_puuid(summoner_name, summoner_tag):
    #url = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={riot_api_key}' 옛 버전
    url = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}?api_key={riot_api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['puuid']
    else:
        return None


#게임 모드의 한국어 반환
def get_game_mode(queue_id: int) -> str:
    game_modes = {
        400: '일반',
        420: '솔로랭크',
        430: '일반',
        440: '자유 5:5 랭크',
        450: '무작위 총력전',
        700: '소환사의 협곡 5:5 랭크',
        710: '일반',
        720: '우르프(URF)',
        830: '솔로 랭크 칼바람 나락',
        900: '모두 무작위 U.R.F.',
        920: '칼바람 나락',
        1900: '선택 U.R.F.'
    }
    if queue_id in game_modes:
        return game_modes[queue_id]
    else:
        return "알 수 없는 게임 모드입니다."

#게임 스펠 한국어
def get_spell_name(summoner_spell_id):
    url = f'https://kr.api.riotgames.com/lol/static-data/v4/summoner-spells/{summoner_spell_id}?locale=ko_KR&api_key={riot_api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['name']
    else:
        return 'Unknown'

#게임 룬 한국어
def get_primary_perk(participant):
    primary_style = participant['perks']['styles'][0]
    for selection in primary_style['selections']:
        if selection['perk'] != 0:
            return selection['perk']
    return None

def get_sub_perk_style(participant):
    sub_style = participant['perks']['styles'][1]
    return sub_style['style']

def get_rune_name(rune_id):
    # 룬 정보를 담을 딕셔너리를 생성합니다.
    RUNE_DICT = {}

    RUNE_URL = f"https://kr.api.riotgames.com/lol/static-data/v4/runes?locale=ko_KR&api_key={riot_api_key}"
    rune_data = requests.get(RUNE_URL).json()

    for rune_id in rune_data["data"].keys():
        rune_name = rune_data["data"][rune_id]["name"]
        RUNE_DICT[int(rune_id)] = rune_name

    print(RUNE_DICT[rune_id])
    return RUNE_DICT[rune_id]

def get_primary_perk(participant):
    primary_style = participant['perks']['styles'][0]
    for selection in primary_style['selections']:
        if selection['perk'] != 0:
            return selection['perk']
    return None

def get_sub_perk_style(participant):
    sub_style = participant['perks']['styles'][1]
    return sub_style['style']

#게임 플레이날짜
def get_time_ago_str(delta):
    """
    입력받은 timedelta 객체를 분 단위로 변환하여 문자열로 반환합니다.
    """
    delta_min = delta.total_seconds() // 60
    if delta_min < 60:
        return f"{int(delta_min)}분 전"
    elif delta_min < 1440:
        return f"{int(delta_min//60)}시간 전"
    else:
        return f"{int(delta_min//1440)}일 전"

# 이미지 다운로드 함수
def download_image(url, filename):
    with open(filename, 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

#전적에서 사용된 챔피언 이미지 URL을 받아오는 함수
def get_champion_image_url(champion_name):
    version = get_version()
    response = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json')
    champions = response.json()['data']

    for champ in champions.values():
        if champ['id'] == champion_name:
            url = f"http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ['image']['full']}"
            return url

#팀 전체 킬수를 가져오는 함수
def get_team_kills(match_id, team_id):
    match_data = get_match_data(match_id)
    team_kills = 0
    for participant in match_data["info"]["participants"]:
        if participant["teamId"] == team_id:
            team_kills += participant["kills"]
    return team_kills

#매치결과 반환
def get_match_data(match_id):
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={riot_api_key}'
    response = requests.get(url)
    return response.json()

#!롤전적 명령어 구현
@client.command(name="롤전적", aliases=['lol_Re'], help='사용법 *롤전적 [소환사명] [태그] [갯수] ')
async def 롤전적(ctx, player_info_num):
    await ctx.send(player_info_num)
    try:
        # 입력된 문자열을 공백을 기준으로 분리
        parts = player_info_num.split()
        
        # 첫 번째 부분은 플레이어 정보
        player_info = parts[0]

        # 나머지 부분은 반복 횟수
        num = int(parts[-1])

        # 만약 플레이어 정보에 #이 포함되어 있다면
        if '#' in player_info:
            player_name, player_tag = player_info.split("#")

            # 공백을 포함한 플레이어 이름을 재구성
            for part in parts[1:]:
                player_name += ' ' + part
        else:
            # #이 포함되어 있지 않다면 전체가 플레이어 이름
            player_name = player_info
            player_tag_num = parts[1]

    except ValueError:
        await ctx.send("전적의 개수는 숫자로 입력해주세요!")
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
                    champ_name_k = get_champion_name(champ_name_e.capitalize())
                    game_duration = info['gameDuration']
                    win = participant['win']
                    kda = f"{participant['kills']} / {participant['deaths']} / {participant['assists']}"

                    double_kill = participant['doubleKills']
                    triple_kill = participant['tripleKills']
                    quadra_kill = participant['quadraKills']
                    penta_kill = participant['pentaKills']

                    # match_info에서 챔피언 이미지를 받아옴
                    champ_image_url = get_champion_image_url(champ_name_e.capitalize())

                    # 이미지 파일 객체를 만듦
                    response = requests.get(champ_image_url)
                    #image_file = File(io.BytesIO(response.content), filename="champion.png")

                    if participant['deaths'] == 0:
                        kda_ratio = "Perfect"
                    else:
                        kda_ratio = round((participant['kills'] + participant['assists']) / participant['deaths'], 2)

                    kill_involvement = (participant['kills'] + participant['assists'] ) / teamKills * 100

                    cs = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
                    cs_str = round(cs / (game_duration/60), 1)

                    spells = [get_spell_name(participant['summoner1Id']), get_spell_name(participant['summoner2Id'])]

                    '''primary_perk = get_rune_name(get_primary_perk(participant))
                    sub_perk_style = get_rune_name(get_sub_perk_style(participant))'''

                    primary_perk = get_primary_perk(participant)
                    sub_perk_style = get_sub_perk_style(participant)

                    '''try:
                        tier = f"{data['tier']} {data['rank']}"
                    except KeyError:
                        tier = "Unranked"'''

                    min = game_duration // 60
                    sec = game_duration % 60

                    time_ago = datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(info['gameCreation']/1000.0)
                    time_ago_str = get_time_ago_str(time_ago)
                    
                    match_info = (f"{game_mode} {'승리' if win else '패배'} {min}분 {sec}초 \n "
                                f"{champ_name_k}  {kda} \t\t\t 평점 {kda_ratio}:1\n"
                                f" \t\t\t 킬관여 {kill_involvement:,.1f}% CS{cs} ({cs_str})\n"
                                f"더블킬:{double_kill} 트리플킬: {triple_kill} 쿼드라킬: {quadra_kill}, 펜타킬: {penta_kill}")
                    
                    embed = discord.Embed(title=f"{summoner_name}님의 최근 {num}판 전적", color=random.randint(0, 0xffffff))
                    embed.add_field(name=f"**Match {idx+1}**", value=match_info, inline=False)
                    embed.set_thumbnail(url=champ_image_url)
                    await ctx.send(embed=embed)
                    break

    '''if match_list:
            
    else:
        await ctx.send("전적 정보를 가져올 수 없습니다. op.gg를 이용해주세요.")'''
        

#버전 정보 
def get_version():
    response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if response.status_code == 200:
        versions = response.json()
        return versions[0]
    
#=============================================================

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
    	await ctx.send("명령어를 찾지 못했습니다")

#=============================================================

client.run("MTA4NTQwNTU4NTI2NjIwMDYzNw.G_R0BJ.VfPqMTAAJWMIQLbQwS8iebRMupgmxgO0N95FYQ")
