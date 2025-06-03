import os
import discord
from discord.ext import commands, tasks
import aiohttp
import json
from dotenv import load_dotenv
from datetime import datetime
import pytz
import asyncio

# Load environment variables
load_dotenv()

# Bot setup with all intents enabled
intents = discord.Intents.all()  # Enable all intents
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


# MTR station codes with their line prefixes
STATIONS = {
    # Tseung Kwan O Line (TKL)
    'north point': {'code': 'TKL-NOP', 'line': 'TKL'},
    'quarry bay': {'code': 'TKL-QUB', 'line': 'TKL'},
    'yau tong': {'code': 'TKL-YAT', 'line': 'TKL'},
    'tiu keng leng': {'code': 'TKL-TIK', 'line': 'TKL'},
    'tseung kwan o': {'code': 'TKL-TKO', 'line': 'TKL'},
    'hang hau': {'code': 'TKL-HAH', 'line': 'TKL'},
    'po lam': {'code': 'TKL-POA', 'line': 'TKL'},
    'lohas park': {'code': 'TKL-LHP', 'line': 'TKL'},

    # Tsuen Wan Line (TWL)
    'tsuen wan': {'code': 'TWL-TSW', 'line': 'TWL'},
    'tai wo hau': {'code': 'TWL-TWH', 'line': 'TWL'},
    'kwai hing': {'code': 'TWL-KWH', 'line': 'TWL'},
    'kwai fong': {'code': 'TWL-KWF', 'line': 'TWL'},
    'lai king': {'code': 'TWL-LAK', 'line': 'TWL'},
    'mei foo': {'code': 'TWL-MEF', 'line': 'TWL'},
    'lai chi kok': {'code': 'TWL-LCK', 'line': 'TWL'},
    'cheung sha wan': {'code': 'TWL-CSW', 'line': 'TWL'},
    'sham shui po': {'code': 'TWL-SSP', 'line': 'TWL'},
    'prince edward': {'code': 'TWL-PRE', 'line': 'TWL'},
    'mong kok': {'code': 'TWL-MOK', 'line': 'TWL'},
    'yau ma tei': {'code': 'TWL-YMT', 'line': 'TWL'},
    'jordan': {'code': 'TWL-JOR', 'line': 'TWL'},
    'tsim sha tsui': {'code': 'TWL-TST', 'line': 'TWL'},
    'admiralty': {'code': 'TWL-ADM', 'line': 'TWL'},
    'central': {'code': 'TWL-CEN', 'line': 'TWL'},

    # Island Line (ISL)
    'kennedy town': {'code': 'ISL-KET', 'line': 'ISL'},
    'hku': {'code': 'ISL-HKU', 'line': 'ISL'},
    'sai ying pun': {'code': 'ISL-SYP', 'line': 'ISL'},
    'sheung wan': {'code': 'ISL-SHW', 'line': 'ISL'},
    'central': {'code': 'ISL-CEN', 'line': 'ISL'},
    'admiralty': {'code': 'ISL-ADM', 'line': 'ISL'},
    'wan chai': {'code': 'ISL-WAC', 'line': 'ISL'},
    'causeway bay': {'code': 'ISL-CAB', 'line': 'ISL'},
    'tin hau': {'code': 'ISL-TIH', 'line': 'ISL'},
    'fortress hill': {'code': 'ISL-FOH', 'line': 'ISL'},
    'north point': {'code': 'ISL-NOP', 'line': 'ISL'},
    'quarry bay': {'code': 'ISL-QUB', 'line': 'ISL'},
    'tai koo': {'code': 'ISL-TAK', 'line': 'ISL'},
    'sai wan ho': {'code': 'ISL-SWH', 'line': 'ISL'},
    'shau kei wan': {'code': 'ISL-SKW', 'line': 'ISL'},
    'heng fa chuen': {'code': 'ISL-HFC', 'line': 'ISL'},
    'chai wan': {'code': 'ISL-CHW', 'line': 'ISL'},

    # Tung Chung Line (TCL)
    'hong kong': {'code': 'TCL-HOK', 'line': 'TCL'},
    'kowloon': {'code': 'TCL-KOW', 'line': 'TCL'},
    'olympic': {'code': 'TCL-OLY', 'line': 'TCL'},
    'nam cheong': {'code': 'TCL-NAC', 'line': 'TCL'},
    'lai king': {'code': 'TCL-LAK', 'line': 'TCL'},
    'tsing yi': {'code': 'TCL-TSY', 'line': 'TCL'},
    'sunny bay': {'code': 'TCL-SUN', 'line': 'TCL'},
    'tung chung': {'code': 'TCL-TUC', 'line': 'TCL'},

    # East Rail Line (EAL)
    'admiralty': {'code': 'EAL-ADM', 'line': 'EAL'},
    'exhibition centre': {'code': 'EAL-EXC', 'line': 'EAL'},
    'hung hom': {'code': 'EAL-HUH', 'line': 'EAL'},
    'mong kok east': {'code': 'EAL-MKK', 'line': 'EAL'},
    'kowloon tong': {'code': 'EAL-KOT', 'line': 'EAL'},
    'tai wai': {'code': 'EAL-TAW', 'line': 'EAL'},
    'sha tin': {'code': 'EAL-SHT', 'line': 'EAL'},
    'fo tan': {'code': 'EAL-FOT', 'line': 'EAL'},
    'university': {'code': 'EAL-UNI', 'line': 'EAL'},
    'tai po market': {'code': 'EAL-TAP', 'line': 'EAL'},
    'tai wo': {'code': 'EAL-TWO', 'line': 'EAL'},
    'fanling': {'code': 'EAL-FAN', 'line': 'EAL'},
    'sheung shui': {'code': 'EAL-SHS', 'line': 'EAL'},
    'lo wu': {'code': 'EAL-LOW', 'line': 'EAL'},
    'lok ma chau': {'code': 'EAL-LMC', 'line': 'EAL'},

    # Tuen Ma Line (TML)
    'wu kai sha': {'code': 'TML-WKS', 'line': 'TML'},
    'ma on shan': {'code': 'TML-MOS', 'line': 'TML'},
    'heng on': {'code': 'TML-HEO', 'line': 'TML'},
    'tai shui hang': {'code': 'TML-TSH', 'line': 'TML'},
    'che kung temple': {'code': 'TML-CKT', 'line': 'TML'},
    'sha tin wai': {'code': 'TML-STW', 'line': 'TML'},
    'city one': {'code': 'TML-CIO', 'line': 'TML'},
    'shek mun': {'code': 'TML-SHM', 'line': 'TML'},
    'tai wai': {'code': 'TML-TAW', 'line': 'TML'},
    'hin keng': {'code': 'TML-HIK', 'line': 'TML'},
    'diamond hill': {'code': 'TML-DIH', 'line': 'TML'},
    'kai tak': {'code': 'TML-KAT', 'line': 'TML'},
    'sung wong toi': {'code': 'TML-SUW', 'line': 'TML'},
    'to kwa wan': {'code': 'TML-TKW', 'line': 'TML'},
    'hung hom': {'code': 'TML-HUH', 'line': 'TML'},
    'east tsim sha tsui': {'code': 'TML-ETS', 'line': 'TML'},
    'austin': {'code': 'TML-AUS', 'line': 'TML'},
    'nam cheong': {'code': 'TML-NAC', 'line': 'TML'},
    'mei foo': {'code': 'TML-MEF', 'line': 'TML'},
    'tsuen wan west': {'code': 'TML-TWW', 'line': 'TML'},
    'kam sheung road': {'code': 'TML-KSR', 'line': 'TML'},
    'yuen long': {'code': 'TML-YUL', 'line': 'TML'},
    'long ping': {'code': 'TML-LOP', 'line': 'TML'},
    'tin shui wai': {'code': 'TML-TIS', 'line': 'TML'},
    'siu hong': {'code': 'TML-SIH', 'line': 'TML'},
    'tuen mun': {'code': 'TML-TUM', 'line': 'TML'},
}

# Line names for better display
LINE_NAMES = {
    'TML': 'Tuen Ma Line',
    'EAL': 'East Rail Line',
    'TCL': 'Tung Chung Line',
    'TKL': 'Tseung Kwan O Line',
    'TWL': 'Tsuen Wan Line',
    'ISL': 'Island Line',
    'AEL': 'Airport Express Line',
    'DRL': 'Disney Resort Line',
    'SIL': 'South Island Line',
}
# Store active station queries
active_queries = {}

async def fetch_mtr_data(station_info):
    """Fetch MTR arrival times for a specific station"""
    station_code = station_info['code']  # Now using the full code directly
    url = f"https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={station_info['line']}&sta={station_code[4:]}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                return None
        except Exception as e:
            print(f"Error fetching MTR data: {e}")
            return None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready to track MTR times!')
    await bot.change_presence(activity=discord.Game(name="!help for commands"))
@bot.command(name='help')
async def help_command(ctx):
    print("!stations - show all stations name")
    print("!mtr <station name> = show the arrival time of that station")

@bot.command(name='stations')
async def stations_command(ctx):
    """List all available stations"""
    # Group stations by line
    stations_by_line = {}
    for station, info in STATIONS.items():
        line_code = info['line']
        if line_code not in stations_by_line:
            stations_by_line[line_code] = []
        stations_by_line[line_code].append(station.title())

    embed = discord.Embed(
        title="📍 Available MTR Stations",
        color=discord.Color.green()
    )

    # Add stations grouped by line
    for line_code, station_list in stations_by_line.items():
        line_name = LINE_NAMES.get(line_code, line_code)
        stations_text = '\n'.join([f"• {station}" for station in sorted(station_list)])
        embed.add_field(
            name=f"🚇 {line_name}",
            value=stations_text,
            inline=False
        )

    embed.set_footer(text="Use !mtr <station name> to get arrival times")
    await ctx.send(embed=embed)

@bot.command(name='mtr')
async def mtr_command(ctx, *, station: str):
    """Get MTR arrival times for a specific station"""
    station = station.lower()
    if station not in STATIONS:
        stations_list = '\n'.join([f"• {s.title()}" for s in sorted(STATIONS.keys())])
        await ctx.send(f"❌ Station not found. Available stations:\n{stations_list}")
        return

    station_info = STATIONS[station]
    data = await fetch_mtr_data(station_info)
    
    if not data or data.get('status') != 1:
        await ctx.send(f"❌ Sorry, couldn't fetch MTR data for {station.title()} at the moment. Please try again later.")
        return

    embed = discord.Embed(
        title=f"🚇 MTR Arrival Times - {station.title()}",
        description=f"Line: {LINE_NAMES.get(station_info['line'], station_info['line'])}",
        color=discord.Color.blue(),
        timestamp=datetime.now(pytz.timezone('Asia/Hong_Kong'))
    )
    
    hk_time = datetime.now(pytz.timezone('Asia/Hong_Kong')).strftime('%H:%M:%S')
    embed.set_footer(text=f"Last updated: {hk_time} (HKT)")

    station_data = data['data'].get(station_info['code'])
    if station_data:
        # Process UP line trains (Northbound)
        if 'UP' in station_data:
            up_text = ""
            for train in station_data['UP'][:3]:  # Show next 3 trains
                dest = train.get('dest', 'Unknown')
                plat = train.get('plat', '?')
                mins = train.get('ttnt', '?')
                if mins == '0':
                    time_text = "Arriving"
                else:
                    time_text = f"{mins} mins"
                up_text += f"→ Platform {plat}: To {dest} in {time_text}\n"
            if up_text:
                embed.add_field(name="🔼 Northbound", value=up_text, inline=False)

        # Process DOWN line trains (Southbound)
        if 'DOWN' in station_data:
            down_text = ""
            for train in station_data['DOWN'][:3]:  # Show next 3 trains
                dest = train.get('dest', 'Unknown')
                plat = train.get('plat', '?')
                mins = train.get('ttnt', '?')
                if mins == '0':
                    time_text = "Arriving"
                else:
                    time_text = f"{mins} mins"
                down_text += f"→ Platform {plat}: To {dest} in {time_text}\n"
            if down_text:
                embed.add_field(name="🔽 Southbound", value=down_text, inline=False)

    if not embed.fields:
        embed.description += "\n\nNo trains scheduled at this time."

    # Add delay information if available
    if data.get('isdelay') == 'Y':
        embed.add_field(name="⚠️ Notice", value="There are delays on this line", inline=False)

    await ctx.send(embed=embed)
    
# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))