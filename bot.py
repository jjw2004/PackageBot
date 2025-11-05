import discord
from discord.ext import commands, tasks
import os
import asyncio
import time
import cv2
from datetime import datetime
from dotenv import load_dotenv

# Try to import Grove sensor libs
try:
    from seeed_dht import DHT
    from grove.gpio import GPIO
    from grove.adc import ADC
    SENSORS_AVAILABLE = True
except Exception:
    SENSORS_AVAILABLE = False

# Load .env
load_dotenv()

# Configuration
PIR_PIN = 16
DHT_PIN = 5
RAIN_CHANNEL = 0
VIDEO_DIR = "/home/joey/package_videos"
MONITORING_CHANNEL_ID = None

# Initialize sensor objects if available
if SENSORS_AVAILABLE:
    try:
        dht = DHT("11", DHT_PIN)
        pir = GPIO(PIR_PIN, GPIO.IN)
        adc = ADC(0x08)
    except Exception as e:
        print(f"Sensor initialization failed: {e}")
        SENSORS_AVAILABLE = False
        dht = None
        pir = None
        adc = None
else:
    dht = None
    pir = None
    adc = None

# Monitoring state
monitoring_active = False
last_motion_time = 0
cooldown_period = 30

# Camera configuration - using both cameras
CAMERA_INDEXES = {
    "outside-camera": 0,  # First USB camera (outside view)
    "inside-camera": 2    # Second USB camera (inside box view)
}

os.makedirs(VIDEO_DIR, exist_ok=True)

# Helper: find all working cameras
def find_working_cameras(max_index=4, timeout=1.0):
    """Find all working camera indexes"""
    working = []
    for idx in range(max_index + 1):
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            cap.release()
            continue
        start = time.time()
        ok = False
        while time.time() - start < timeout:
            ret, frame = cap.read()
            if ret and frame is not None:
                ok = True
                break
            time.sleep(0.05)
        cap.release()
        if ok:
            working.append(idx)
    return working

# Video recording function - records from both cameras
async def record_video_dual(duration=5, fps=15):
    """Record from both cameras simultaneously and return both video paths"""
    print(f"🎥 Recording {duration}s from both cameras at {fps} fps...")
    
    video_paths = {}
    
    for camera_label, camera_idx in CAMERA_INDEXES.items():
        cap = cv2.VideoCapture(camera_idx)
        if not cap.isOpened():
            print(f"❌ Cannot open {camera_label} (index {camera_idx})")
            continue

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mp4_path = os.path.join(VIDEO_DIR, f"{camera_label}_{timestamp}.mp4")
        avi_path = os.path.join(VIDEO_DIR, f"{camera_label}_{timestamp}.avi")

        # Try MP4
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(mp4_path, fourcc, float(fps), (width, height))
        out_path = mp4_path
        if not out.isOpened():
            try:
                out.release()
            except:
                pass
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(avi_path, fourcc, float(fps), (width, height))
            out_path = avi_path
            if not out.isOpened():
                print(f"❌ VideoWriter failed for {camera_label}")
                cap.release()
                continue

        # Record video
        start = time.time()
        frames = 0
        while time.time() - start < duration:
            ret, frame = cap.read()
            if not ret or frame is None:
                print(f"❌ Failed to read frame from {camera_label}")
                break
            out.write(frame)
            frames += 1
        
        cap.release()
        out.release()
        print(f"✅ Saved {camera_label}: {out_path} ({frames} frames)")
        video_paths[camera_label] = out_path

    return video_paths if video_paths else None

# Sensor reading
def get_sensor_data():
    if not SENSORS_AVAILABLE or dht is None:
        return {"temperature": "N/A", "humidity": "N/A", "rain_status": "N/A", "rain_value": 0}
    try:
        # read DHT (some libraries return (temperature, humidity) or (humidity, temperature))
        reading = dht.read()
        # normalize to (humidity, temperature) if needed
        if isinstance(reading, tuple) and len(reading) >= 2:
            humi, temp = reading[0], reading[1]
        else:
            # unexpected format
            humi, temp = None, None

        rain_value = adc.read(RAIN_CHANNEL) if adc is not None else 0
        is_raining = rain_value > 500 if adc is not None else False
        return {"temperature": temp if temp is not None else "N/A",
                "humidity": humi if humi is not None else "N/A",
                "rain_status": "Raining" if is_raining else "Dry",
                "rain_value": rain_value}
    except Exception as e:
        print(f"Sensor read failed: {e}")
        return {"temperature": "Error", "humidity": "Error", "rain_status": "Error", "rain_value": 0}

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} connected")
    if not package_monitor.is_running():
        package_monitor.start()
        print("🔄 Package monitoring loop started")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency*1000)}ms')

@bot.command(name='info')
async def info(ctx):
    # Provide detailed sensor readings similar to the previous bot behavior
    data = get_sensor_data()
    # Determine motion state
    motion_state = "Unknown"
    try:
        if pir is not None:
            try:
                pv = pir.read()
            except Exception:
                pv = getattr(pir, 'value', lambda: None)()
            motion_state = "🚶 Motion" if pv == 1 else "😴 No Motion"
        else:
            motion_state = "😴 No Motion"
    except Exception:
        motion_state = "Unknown"

    embed = discord.Embed(title="PackageBot", description="🔬 Current Sensor Readings", color=0x00ff00)
    embed.add_field(name="🌡️ Temperature", value=f"{data['temperature']}°C", inline=False)
    embed.add_field(name="💧 Humidity", value=f"{data['humidity']}%", inline=False)
    embed.add_field(name="🌧️ Weather", value=f"{data['rain_status']}", inline=False)
    embed.add_field(name="💧 Rain Value", value=str(data.get('rain_value', 0)), inline=False)
    embed.add_field(name="� Motion", value=motion_state, inline=False)
    await ctx.send(embed=embed)

@bot.command(name='say')
async def say(ctx, *, message: str):
    await ctx.send(message)

@bot.command(name='sensors')
async def sensors_cmd(ctx):
    data = get_sensor_data()
    embed = discord.Embed(title="Sensor Readings", color=0x0099ff)
    embed.add_field(name="Temperature", value=f"{data['temperature']}°C", inline=True)
    embed.add_field(name="Humidity", value=f"{data['humidity']}%", inline=True)
    embed.add_field(name="Rain", value=f"{data['rain_status']}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='testvideo')
async def testvideo(ctx):
    if not SENSORS_AVAILABLE:
        await ctx.send("❌ Sensors not available")
        return
    await ctx.send("🎥 Recording 5s test video from both cameras...")
    video_paths = await record_video_dual(5)
    if video_paths:
        for camera_label, path in video_paths.items():
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        await ctx.send(f"✅ {camera_label} video:", file=discord.File(f, filename=os.path.basename(path)))
                    # Delete video after successful upload
                    os.remove(path)
                    print(f"🗑️ Deleted {path} after upload")
                except Exception as e:
                    await ctx.send(f"Failed to send {camera_label} video: {e}")
            else:
                await ctx.send(f"❌ {camera_label} video file not found")
    else:
        await ctx.send("❌ Failed to record test videos")

@bot.command(name='monitor')
async def monitor_cmd(ctx, action: str = 'status'):
    global monitoring_active, MONITORING_CHANNEL_ID
    if action == 'start':
        if not SENSORS_AVAILABLE:
            await ctx.send("❌ Sensors not available")
            return
        monitoring_active = True
        MONITORING_CHANNEL_ID = ctx.channel.id
        await ctx.send("📦 Monitoring started in this channel")
    elif action == 'stop':
        monitoring_active = False
        MONITORING_CHANNEL_ID = None
        await ctx.send("📦 Monitoring stopped")
    else:
        await ctx.send(f"Monitoring: {'active' if monitoring_active else 'inactive'}")

@tasks.loop(seconds=0.5)
async def package_monitor():
    global last_motion_time
    if not monitoring_active or not SENSORS_AVAILABLE:
        return
    try:
        pir_value = None
        if pir is not None:
            try:
                pir_value = pir.read()
            except Exception:
                try:
                    pir_value = pir.value()
                except Exception:
                    pir_value = None
        if pir_value == 1:
            now = time.time()
            if now - last_motion_time > cooldown_period:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = get_sensor_data()
                video_paths = await record_video_dual(10, fps=15)
                # send to channel
                ch = bot.get_channel(MONITORING_CHANNEL_ID)
                if ch:
                    embed = discord.Embed(title='📦 Package Delivery', description=f'Motion detected at {timestamp}', color=0x00ff00)
                    embed.add_field(name='🌡️ Temp', value=f"{data['temperature']}°C", inline=True)
                    embed.add_field(name='💧 Humidity', value=f"{data['humidity']}%", inline=True)
                    embed.add_field(name='🌧️ Weather', value=data['rain_status'], inline=True)
                    await ch.send(embed=embed)
                    # Send both videos and delete after upload
                    if video_paths:
                        for camera_label, path in video_paths.items():
                            if os.path.exists(path):
                                try:
                                    with open(path, 'rb') as f:
                                        await ch.send(f"📹 {camera_label}:", file=discord.File(f, filename=os.path.basename(path)))
                                    # Delete video after successful upload
                                    os.remove(path)
                                    print(f"🗑️ Deleted {path} after upload")
                                except Exception as e:
                                    print(f"Failed to upload/delete {camera_label}: {e}")
                last_motion_time = now
    except Exception as e:
        print(f"Monitor error: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found")
    else:
        print(f"Command error: {error}")

if __name__ == '__main__':
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print('DISCORD_BOT_TOKEN missing in .env')
    else:
        bot.run(token)