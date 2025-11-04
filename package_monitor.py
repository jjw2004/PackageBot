#!/usr/bin/env python3
"""
Simple Package Delivery Monitor
Records video when motion detected and sends to Discord
"""
import time
import cv2
import os
from datetime import datetime
from seeed_dht import DHT
from grove.gpio import GPIO
from grove.adc import ADC
import requests

# Configuration
PIR_PIN = 16  # Motion sensor
DHT_PIN = 5   # Temperature sensor  
RAIN_CHANNEL = 0  # Rain sensor
VIDEO_DIR = "/home/joey/package_videos"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1418157881815207936/KtlVrXDwRzC95CMKYTeH6MTGLI1BGEuWzRlQKLo1syKatB7RRwlVeEpr2BZye2iej28b"  # Replace with your webhook URL from Discord

# Setup sensors
pir = GPIO(PIR_PIN, GPIO.IN)
dht = DHT("11", DHT_PIN)
adc = ADC(0x08)

# Create video directory
os.makedirs(VIDEO_DIR, exist_ok=True)

def record_video(duration=10):
    """Record a video for specified duration"""
    print(f"🎥 Recording {duration} second video...")
    
    # Setup camera
    cap = cv2.VideoCapture(0)  # Use USB camera
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return None
    
    # Video settings
    fps = 20
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create video filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"delivery_{timestamp}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    # Record video
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            frame_count += 1
        else:
            break
    
    # Cleanup
    cap.release()
    out.release()
    
    print(f"✅ Video saved: {video_path} ({frame_count} frames)")
    return video_path

def get_sensor_data():
    """Get current sensor readings"""
    # Temperature and humidity
    humi, temp = dht.read()
    
    # Rain detection
    rain_value = adc.read(RAIN_CHANNEL)
    is_raining = rain_value > 500
    
    return {
        "temperature": temp if temp is not None else "N/A",
        "humidity": humi if humi is not None else "N/A", 
        "rain_status": "Raining" if is_raining else "Dry",
        "rain_value": rain_value
    }

def send_to_discord(video_path, sensor_data, timestamp):
    """Send delivery notification to Discord"""
    if not DISCORD_WEBHOOK_URL or "YOUR_DISCORD_WEBHOOK_URL_HERE" in DISCORD_WEBHOOK_URL:
        print("⚠️  Discord webhook not configured - skipping upload")
        return
    
    try:
        # Create message
        message = {
            "content": "📦 **Package Delivery Detected!**",
            "embeds": [{
                "title": "🚚 Delivery Alert",
                "description": f"Motion detected at {timestamp}",
                "color": 0x00ff00,
                "fields": [
                    {"name": "🌡️ Temperature", "value": f"{sensor_data['temperature']}°C", "inline": True},
                    {"name": "💧 Humidity", "value": f"{sensor_data['humidity']}%", "inline": True},
                    {"name": "🌧️ Weather", "value": sensor_data['rain_status'], "inline": True}
                ],
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        # Send message first
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        
        # Send video file
        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(DISCORD_WEBHOOK_URL, files=files)
        
        print("✅ Sent to Discord!")
        
    except Exception as e:
        print(f"❌ Failed to send to Discord: {e}")

def main():
    """Main monitoring loop"""
    print("📦 Package Delivery Monitor Started")
    print("===================================")
    print(f"Motion sensor: D{PIR_PIN}")
    print(f"Temperature sensor: D{DHT_PIN}")
    print(f"Rain sensor: A{RAIN_CHANNEL}")
    print(f"Video directory: {VIDEO_DIR}")
    print("\nWaiting for motion... (Ctrl+C to stop)")
    
    last_motion_time = 0
    cooldown_period = 30  # 30 seconds between recordings
    
    try:
        while True:
            # Check for motion
            if pir.read() == 1:
                current_time = time.time()
                
                # Check cooldown to prevent spam
                if current_time - last_motion_time > cooldown_period:
                    print(f"\n🚶 MOTION DETECTED!")
                    
                    # Get timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"📅 Time: {timestamp}")
                    
                    # Get sensor data
                    sensor_data = get_sensor_data()
                    print(f"🌡️  Temperature: {sensor_data['temperature']}°C")
                    print(f"💧 Humidity: {sensor_data['humidity']}%")
                    print(f"🌧️  Weather: {sensor_data['rain_status']}")
                    
                    # Record video
                    video_path = record_video(10)
                    
                    # Send to Discord
                    send_to_discord(video_path, sensor_data, timestamp)
                    
                    last_motion_time = current_time
                    print("⏳ Cooldown active for 30 seconds...")
                
            time.sleep(0.5)  # Check every 500ms
            
    except KeyboardInterrupt:
        print(f"\n\n📦 Package Monitor Stopped")
        print("Thanks for using Package Delivery Monitor!")

if __name__ == "__main__":
    main()