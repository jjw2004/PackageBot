import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Set bot status (optional)
    await bot.change_presence(activity=discord.Game(name="Type !help for commands"))

@bot.event
async def on_message(message):
    """Called when a message is sent in any channel the bot can see"""
    # Don't respond to the bot's own messages
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)

# Basic Commands
@bot.command(name='hello')
async def hello_command(ctx):
    """Says hello to the user"""
    await ctx.send(f'Hello {ctx.author.mention}! 👋')

@bot.command(name='ping')
async def ping_command(ctx):
    """Check bot's latency"""
    latency = round(bot.latency * 1000)  # Convert to milliseconds
    await ctx.send(f'Pong! 🏓 Latency: {latency}ms')

@bot.command(name='info')
async def info_command(ctx):
    """Display bot information"""
    embed = discord.Embed(
        title="PackageBot Info",
        description="A Discord bot created with discord.py",
        color=0x00ff00
    )
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='say')
async def say_command(ctx, *, message):
    """Make the bot say something"""
    await ctx.send(message)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument! Check the command usage with `!help`")
    else:
        print(f"An error occurred: {error}")
        await ctx.send("❌ An unexpected error occurred!")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token is None:
        print("❌ Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
    else:
        bot.run(token)