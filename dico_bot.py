import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
import tempfile
import shutil # shutil 임포트 추가

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()
if OPENAI_API_KEY:
    client.api_key = OPENAI_API_KEY
else:
    print("경고: OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다. TTS 기능이 제한될 수 있습니다.")

# Define Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Define Bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# 전역 변수
current_vc = None  # 현재 연결된 음성 클라이언트
listening_text_channel_id = None # 봇이 메시지를 읽을 텍스트 채널 ID
ffmpeg_executable_path = "ffmpeg" # FFmpeg 실행 파일 이름 또는 전체 경로
AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
current_tts_voice = "alloy" # 기본 목소리

async def play_tts_in_vc(vc: discord.VoiceClient, text_to_say: str, ctx_for_feedback=None):
    """지정된 음성 클라이언트에서 TTS를 재생합니다."""
    if not vc or not vc.is_connected():
        feedback_message = "봇이 음성 채널에 연결되어 있지 않습니다."
        # ctx_for_feedback이 Messageable 객체인지 확인 (TextChannel, User, Member 등)
        if hasattr(ctx_for_feedback, 'send'): await ctx_for_feedback.send(feedback_message)
        else: print(feedback_message)
        return False

    if vc.is_playing():
        feedback_message = "이미 다른 내용을 말하고 있어요. 잠시 후 다시 시도해주세요."
        if hasattr(ctx_for_feedback, 'send'): await ctx_for_feedback.send(feedback_message)
        else: print(feedback_message)
        return False

    if hasattr(ctx_for_feedback, 'send'):
        # f-string 따옴표 수정
        await ctx_for_feedback.send(f'잠시만 기다려주세요: "{text_to_say}"')

    def tts_sync():
        try:
            response = client.audio.speech.create(
                model="tts-1", voice=current_tts_voice, input=text_to_say
            )
            return response.content
        except Exception as e:
            print(f"OpenAI TTS API 오류: {e}")
            return None

    audio_content = await bot.loop.run_in_executor(None, tts_sync)

    if not audio_content:
        feedback_message = "TTS 오디오를 생성하는 데 실패했습니다."
        if hasattr(ctx_for_feedback, 'send'): await ctx_for_feedback.send(feedback_message)
        else: print(feedback_message)
        return False

    filename = None
    play_success = False
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(audio_content)
            filename = f.name
        
        if not os.path.exists(filename):
            feedback_message = "오디오 파일 생성에 실패했습니다 (파일 없음)."
            if hasattr(ctx_for_feedback, 'send'): await ctx_for_feedback.send(feedback_message)
            else: print(feedback_message)
            return False
        
        source = discord.FFmpegPCMAudio(filename, executable=ffmpeg_executable_path)
        
        # 재생 완료 후 파일 삭제를 위한 콜백 함수
        def after_playing(error):
            if error:
                print(f'재생 오류: {error}')
            else:
                print('재생 완료.')
            # 파일을 삭제하기 전에 asyncio.create_task를 사용하여 비동기적으로 처리
            # 또는 bot.loop.call_soon_threadsafe 사용 고려
            # 여기서는 간단히 os.remove를 시도하지만, 권한 문제가 발생할 수 있음
            if filename and os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"임시 파일 '{filename}' 삭제 완료.")
                except Exception as e_del:
                    print(f"임시 파일 '{filename}' 삭제 중 오류: {e_del}")

        vc.play(source, after=after_playing)
        play_success = True

    except Exception as e:
        error_message = f"오디오 재생 중 오류: {e}"
        print(error_message)
        if hasattr(ctx_for_feedback, 'send'): await ctx_for_feedback.send("오디오를 재생하는 중에 오류가 발생했습니다.")
        play_success = False
        # 오류 발생 시에도 파일이 생성되었을 수 있으므로 삭제 시도
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e_del:
                print(f"오류 후 임시 파일 '{filename}' 삭제 중 오류: {e_del}")
    # finally 블록에서 파일 삭제 로직은 after 콜백으로 이전했으므로 제거 또는 수정
    return play_success


@bot.event
async def on_ready():
    # global current_vc # on_ready에서는 current_vc를 직접 수정하지 않으므로 global 선언 불필요
    print(f"{bot.user} 연결 완료!")
    # .env 파일에서 TARGET_TEXT_CHANNEL_ID, TARGET_VOICE_CHANNEL_ID 읽는 부분은
    # 사용자의 새 요구사항에 따라 제거되었으므로 관련 로직도 제거합니다.
    print("봇이 메시지를 읽을 텍스트 채널을 설정하려면 `!set_listen_channel #채널명` 또는 `!set_listen_channel 채널이름` 명령어를 사용하세요.")
    print("봇을 음성 채널에 참여시키려면 `!join` 또는 `!join 채널이름` 명령어를 사용하세요.")
    print(f"현재 TTS 목소리: {current_tts_voice}. 변경하려면 `!목소리 목소리이름`을 사용하세요.")
    print("사용 가능한 목소리 목록은 `!voices` 명령어로 확인할 수 있습니다.")


@bot.event
async def on_message(message: discord.Message):
    global current_vc, listening_text_channel_id # 전역 변수 사용 명시

    if message.author == bot.user or message.author.bot:
        return

    # 명령어 처리 (가장 먼저 실행되어야 함)
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return # 명령어가 처리되었으면 이후 로직 실행 안 함

    # 설정된 리스닝 채널의 메시지인지 확인
    if listening_text_channel_id and message.channel.id == listening_text_channel_id:
        if not message.author.voice or not message.author.voice.channel:
            print(f"메시지 작성자 '{message.author.name}'가 음성 채널에 없습니다. TTS를 스킵합니다.")
            # 필요시 사용자에게 알림: await message.channel.send("음성 채널에 먼저 참여해주세요.")
            return

        user_voice_channel = message.author.voice.channel

        # 봇 음성 채널 연결 또는 이동 로직
        if not current_vc or not current_vc.is_connected():
            try:
                current_vc = await user_voice_channel.connect()
                print(f"사용자 '{message.author.name}'의 음성 채널 '{user_voice_channel.name}'에 연결했습니다.")
            except Exception as e:
                print(f"음성 채널 '{user_voice_channel.name}' 연결 중 오류: {e}")
                await message.channel.send(f"음성 채널 '{user_voice_channel.name}'에 연결 중 오류가 발생했습니다: {e}")
                return
        elif current_vc.channel != user_voice_channel:
            try:
                await current_vc.move_to(user_voice_channel)
                print(f"사용자 '{message.author.name}'의 음성 채널 '{user_voice_channel.name}'으로 이동했습니다.")
            except Exception as e:
                print(f"음성 채널 '{user_voice_channel.name}'으로 이동 중 오류: {e}")
                await message.channel.send(f"음성 채널 '{user_voice_channel.name}'으로 이동 중 오류가 발생했습니다: {e}")
                return
        
        if current_vc and current_vc.is_connected():
            print(f"채널({message.channel.name}) 메시지 수신: '{message.content}' -> TTS 시도")
            # play_tts_in_vc 호출 시 ctx_for_feedback으로 message.channel 전달
            await play_tts_in_vc(current_vc, message.content, message.channel) 
        else:
            print("알 수 없는 이유로 음성 채널에 연결되지 않았습니다. TTS를 스킵합니다.")
            await message.channel.send("봇이 음성 채널에 정상적으로 연결되지 않아 TTS를 재생할 수 없습니다.")


@bot.command(name='채널', help="봇이 메시지를 읽을 텍스트 채널을 설정합니다. 예: !set_listen_channel #일반 또는 !set_listen_channel 일반")
async def set_listen_channel_command(ctx, channel_input: discord.TextChannel = None): # 타입 힌트 사용
    global listening_text_channel_id
    
    if channel_input:
        listening_text_channel_id = channel_input.id
        await ctx.send(f"이제부터 '{channel_input.name}' 채널의 메시지를 읽습니다.")
        print(f"리스닝 채널이 '{channel_input.name}' (ID: {channel_input.id})로 설정되었습니다.")
    else:
        await ctx.send("올바른 텍스트 채널을 멘션하거나 채널 이름을 정확히 입력해주세요. 예: `!set_listen_channel #채널명`")

@bot.command(name='목소리', help=f"TTS 목소리를 변경합니다. 사용 가능한 목소리: {', '.join(AVAILABLE_VOICES)}")
async def 목소리리_command(ctx, voice_name: str):
    global current_tts_voice
    if voice_name.lower() in AVAILABLE_VOICES:
        current_tts_voice = voice_name.lower()
        await ctx.send(f"TTS 목소리가 '{current_tts_voice}'(으)로 변경되었습니다.")
        print(f"TTS 목소리가 '{current_tts_voice}'(으)로 변경되었습니다.")
    else:
        await ctx.send(f"잘못된 목소리 이름입니다. 사용 가능한 목소리: {', '.join(AVAILABLE_VOICES)}\n`!voices` 명령어로 자세한 정보를 확인하세요.")

@bot.command(name='목록', help="사용 가능한 TTS 목소리 목록을 보여줍니다.")
async def voices_command(ctx):
    voice_list_message = "사용 가능한 TTS 목소리 목록입니다. `!목소리 [목소리이름]`으로 설정할 수 있습니다.\n"
    for voice in AVAILABLE_VOICES:
        voice_list_message += f"- {voice}\n"
    # 목소리 특징에 대한 설명은 OpenAI 문서를 참고하거나, 각 목소리를 직접 들어보고 추가하는 것이 좋습니다.
    # 예시: voice_list_message += "\n- alloy: 따뜻하고 중후한 남성 목소리 (예시 설명)"
    # voice_list_message += "\n- echo: 활기차고 명랑한 여성 목소리 (예시 설명)"
    # voice_list_message += "\n- fable: 부드럽고 감미로운 남성 목소리 (예시 설명)"
    # voice_list_message += "\n- onyx: 깊고 차분한 남성 목소리 (예시 설명)"
    # voice_list_message += "\n- nova: 밝고 경쾌한 여성 목소리 (예시 설명)"
    # voice_list_message += "\n- shimmer: 속삭이는 듯한 부드러운 여성 목소리 (예시 설명)"
    voice_list_message += "\n각 목소리의 특징은 직접 들어보시는 것을 추천합니다."
    await ctx.send(voice_list_message)

@bot.command(name='join', help="봇을 현재 사용자의 음성 채널 또는 지정된 음성 채널에 참여시킵니다.")
async def join_voice_channel(ctx, *, channel_name: str = None):
    global current_vc
    
    target_voice_channel = None
    if channel_name:
        target_voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
        if not target_voice_channel:
            await ctx.send(f"음성 채널 '{channel_name}'을(를) 찾을 수 없습니다.")
            return
    elif ctx.author.voice and ctx.author.voice.channel:
        target_voice_channel = ctx.author.voice.channel
    else:
        await ctx.send("음성 채널에 먼저 참여하시거나, 참여할 음성 채널 이름을 지정해주세요.")
        return

    if current_vc and current_vc.is_connected():
        if current_vc.channel == target_voice_channel:
            await ctx.send(f"이미 '{target_voice_channel.name}' 채널에 있습니다.")
        else:
            try:
                await current_vc.move_to(target_voice_channel)
                await ctx.send(f"'{target_voice_channel.name}' 채널로 이동했습니다.")
            except Exception as e:
                await ctx.send(f"'{target_voice_channel.name}' 채널로 이동 중 오류: {e}")
    else:
        try:
            current_vc = await target_voice_channel.connect()
            await ctx.send(f"'{target_voice_channel.name}' 채널에 연결했습니다.")
        except Exception as e:
            await ctx.send(f"'{target_voice_channel.name}' 채널 연결 중 오류: {e}")

@bot.command(name='leave', help="봇을 현재 음성 채널에서 내보냅니다.")
async def leave_voice_channel(ctx):
    global current_vc
    if current_vc and current_vc.is_connected():
        await current_vc.disconnect()
        current_vc = None 
        await ctx.send("음성 채널 연결을 종료했습니다.")
    else:
        await ctx.send("연결된 음성 채널이 없습니다.")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def say(ctx, *, text: str):
    global current_vc
    if not current_vc or not current_vc.is_connected():
        if ctx.author.voice and ctx.author.voice.channel:
            user_vc = ctx.author.voice.channel
            print(f"!say 명령어: 사용자의 음성 채널 '{user_vc.name}'에 연결 시도")
            try:
                current_vc = await user_vc.connect()
                await ctx.send(f"'{user_vc.name}' 채널에 연결했습니다.")
            except Exception as e:
                await ctx.send(f"음성 채널 '{user_vc.name}' 연결 중 오류: {e}")
                return 
        else:
            await ctx.send("봇이 음성 채널에 없거나, 당신도 음성 채널에 없습니다. `!join` 명령어로 봇을 참여시키거나 음성 채널에 먼저 입장해주세요.")
            return
    
    if current_vc and current_vc.is_connected():
        # say 명령어의 경우 ctx를 feedback context로 전달
        await play_tts_in_vc(current_vc, text, ctx) 
    else:
        await ctx.send("음성 채널에 연결되어 있지 않아 TTS를 재생할 수 없습니다.")

if __name__ == "__main__":
    # .env 파일에서 TOKEN, OPENAI_API_KEY 로드 확인
    TOKEN = os.getenv("DISCORD_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not TOKEN:
        print("오류: DISCORD_TOKEN이 .env 파일에 설정되지 않았습니다.")
        exit()
    if not OPENAI_API_KEY:
        print("오류: OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다.")
        # OpenAI API 키가 필수는 아니라고 판단되면 이 부분을 주석 처리하거나 로직 변경
        # exit() 
        # print("경고: OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다. TTS 기능이 제한될 수 있습니다.") # 이 부분은 위로 이동했습니다.

    # client.api_key = OPENAI_API_KEY # OpenAI 클라이언트에 API 키 설정 # 이 부분은 위로 이동했습니다.

    if not shutil.which(ffmpeg_executable_path): # shutil.which를 사용하여 FFmpeg 확인
         print(f"경고: FFmpeg 실행 파일 '{ffmpeg_executable_path}'을(를) 시스템 PATH에서 찾을 수 없습니다.")
         print("FFmpeg가 설치되어 있고, 시스템 PATH에 올바르게 설정되어 있는지 확인해주세요.")
         if os.name == 'nt':
             print(f"Windows의 경우, FFmpeg를 다운로드하여 PATH에 추가하거나, 코드 상단의 ffmpeg_executable_path 변수에 'ffmpeg.exe'의 전체 경로를 지정해야 합니다.")
         else:
             print(f"Linux/macOS의 경우, 'sudo apt install ffmpeg' (Debian/Ubuntu) 또는 'brew install ffmpeg' (macOS) 등으로 설치할 수 있습니다.")
         # FFmpeg를 찾지 못해도 일단 봇 실행은 계속하도록 exit()는 주석 처리 또는 제거
         # exit() 

    bot.run(TOKEN)