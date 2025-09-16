# 🤖 discordbot-py

간단한 **디스코드 학습용 봇(Discord Bot)** 프로젝트입니다.  
Python으로 디스코드 API를 연습하고 토큰/환경변수 관리, 배포 흐름까지 익히는 것을 목표로 했습니다.

---

## 🔧 요구사항(Prerequisites)

- Python 3.10+ (권장)
- Git
- (로컬 실행 시) 디스코드 봇 토큰

---

## 📦 설치 & 실행

1) 저장소 클론
```bash
git clone https://github.com/sopo9880/discordbot-py.git
cd discordbot-py
````

2. 가상환경 생성 & 활성화

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. 환경변수 설정 (둘 중 하나)

* **A. .env 사용 (권장)**
  루트에 `.env` 파일 생성:

  예시:
  ```env
  DISCORD_BOT_TOKEN=여기에_디스코드_봇_토큰
  ```

  코드에서 `python-dotenv`를 사용한다면 자동 로드되거나, 아래처럼 수동으로 불러올 수 있습니다:

  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

> ⚠️ 코드에서 읽는 변수명이 `DISCORD_BOT_TOKEN`, `DISCORD_TOKEN`, `TOKEN` 등으로 다를 수 있습니다.
> `discordbot.py` 내부에서 `os.getenv(...)`에 사용하는 **키 이름**을 확인하여 맞춰주세요.

5. 실행

```bash
python discordbot.py
```

---

## 🗂️ 프로젝트 구조(예시)

```
discordbot-py/
├─ discordbot.py         # 봇 메인 진입 파일
├─ requirements.txt      # 파이썬 의존성
├─ Pipfile               # (Pipenv 사용 시)
└─ Pipfile.lock
```

---

## ✨ 지금까지 구현/연습 포인트(예시)

* 디스코드 봇 접속/이벤트 루프 기본
* 간단한 커맨드(예: ping)
* 환경변수/토큰을 코드 밖에서 안전하게 관리하는 법
* 요구사항 파일로 재현성 있는 실행 환경 구성

> 실제 제공 명령어와 기능은 `discordbot.py`를 참고하세요. 필요에 따라 슬래시 커맨드로 전환하거나 Cog 구조로 모듈화할 수 있습니다.

---

## 🧪 개발 팁

* 커밋 전에 **토큰이 커밋되지 않았는지** 반드시 확인하세요.
  `.gitignore`에 `.env` 추가:

  ```
  .env
  __pycache__/
  .pytest_cache/
  .vscode/
  .DS_Store
  ```
* 과거 커밋에 토큰이 포함되었으면 `git filter-repo`/BFG로 **히스토리를 재작성**해 완전히 제거하세요.
* `requirements.txt` 업데이트:

  ```bash
  pip freeze > requirements.txt
  ```

---
