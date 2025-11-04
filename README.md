# PackageBot 📦

A smart package delivery monitoring system built with Python, Discord.py, and Raspberry Pi. PackageBot uses dual cameras and Grove sensors to detect package deliveries and automatically send video recordings with environmental data to Discord.

![Bot Avatar](PackageBot-pfp.png)

## 🌟 Features

- **Dual Camera Recording** - Simultaneously records from two USB cameras (outside porch view + inside box view)
- **Motion Detection** - PIR sensor triggers automatic recording when movement is detected
- **Environmental Monitoring** - Tracks temperature, humidity, and rain conditions during deliveries
- **Discord Integration** - Automatically uploads videos and sensor data to your Discord server
- **Real-time Commands** - Interactive bot commands for testing and monitoring control

## 📋 Current Commands

| Command | Description | Usage |
|---------|-------------|--------|
| `!hello` | Greets the user | `!hello` |
| `!ping` | Shows bot latency | `!ping` |
| `!info` | Shows detailed sensor readings (temp, humidity, weather, motion) | `!info` |
| `!sensors` | Quick sensor status check | `!sensors` |
| `!say` | Makes the bot repeat a message | `!say Hello World!` |
| `!testvideo` | Records 5s test video from both cameras | `!testvideo` |
| `!monitor start` | Starts package monitoring in the current channel | `!monitor start` |
| `!monitor stop` | Stops package monitoring | `!monitor stop` |
| `!monitor` | Shows monitoring status | `!monitor` |
| `!help` | Shows all available commands | `!help` |

## 🔧 Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- 2x USB Cameras
- Grove Base Hat for Raspberry Pi
- Grove PIR Motion Sensor (connected to D16)
- Grove DHT11 Temperature & Humidity Sensor (connected to D5)
- Grove Rain/Moisture Sensor (connected to A0)

## 🛠️ Built With

- **Python 3.9** - Programming language
- **discord.py** - Discord API wrapper
- **OpenCV** - Video capture and processing
- **Grove.py** - Seeed Studio Grove sensor libraries
- **python-dotenv** - Environment variable management

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/jjw2004/PackageBot.git
cd PackageBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Discord bot token:
   - Create a `.env` file based on `.env.example`
   - Add your Discord bot token: `DISCORD_BOT_TOKEN=your_token_here`

4. Run the bot:
```bash
python3 bot.py
```

## 🎥 How It Works

1. **Motion Detected** - PIR sensor detects movement near your package delivery area
2. **Dual Recording** - Both cameras start recording simultaneously:
   - Outside camera captures the delivery person approaching
   - Inside camera captures the package being placed in the box
3. **Sensor Data** - Collects temperature, humidity, and weather conditions
4. **Discord Upload** - Sends an embed with sensor data plus both video files to your Discord channel

## 📁 Project Structure

```
PackageBot/
├── bot.py                 # Main Discord bot with dual camera support
├── package_monitor.py     # Standalone monitoring script (legacy)
├── config.py             # Configuration file
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not tracked)
├── .env.example          # Example environment file
└── README.md             # This file
```

## 🎓 Learning Journey

This project combines:
- Discord bot development with async programming
- Computer vision and multi-camera recording
- IoT sensor integration on Raspberry Pi
- Real-time monitoring systems
- Git and version control

## 📝 Project Notes

**Recent Updates:**
- ✅ Dual camera system implementation (Nov 2024)
- ✅ Grove sensor integration (DHT11, PIR, Rain sensor)
- ✅ Async video recording from multiple cameras
- ✅ Enhanced Discord embeds with sensor data

## 🔮 Future Plans

- Add timestamp overlays on videos
- Implement motion detection zones
- Add notification cooldown configuration
- Create web dashboard for viewing recordings
- Add support for more sensor types

## 📚 Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Grove.py Documentation](https://github.com/Seeed-Studio/grove.py)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)

## ⚙️ Configuration

Camera assignments in `bot.py`:
- `outside-camera`: Index 0 (outside/porch view)
- `inside-camera`: Index 2 (inside box view)

Sensor pins:
- PIR Motion: D16
- DHT11 Temp/Humidity: D5  
- Rain Sensor: A0 (ADC 0x08)

---

*Student Project - Fall 2025*
*Built with 🤖 for learning IoT, computer vision, and bot development*
