import discord
from discord.ext import commands
import random
import time
from datetime import datetime
import json
import os 


TOKEN = os.environ.get('DISCORD_TOKEN') 


DATA_FILE = 'ice_ledger.json'


STARTING_ICE = 5000
DAILY_MIN = 500
DAILY_MAX = 1000
DAILY_COOLDOWN_SECONDS = 24 * 60 * 60 
ICE_EMOJI = '❄️'


user_data = {}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


def load_data():
    """Loads user data from the JSON file on bot startup."""
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
               
                data = json.load(f)
                user_data = {int(k): v for k, v in data.items()}
                print(f"Loaded {len(user_data)} users from {DATA_FILE}")
        except Exception as e:
            print(f"Error loading data: {e}. Starting with empty ledger.")
            user_data = {}

def save_data():
    """Saves user data to the JSON file after any modification."""
    try:
       
        data_to_save = {str(k): v for k, v in user_data.items()}
        with open(DATA_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")


def get_user_data(user_id):
    """Retrieves user data or initializes a new user."""
    if user_id not in user_data:
        user_data[user_id] = {
            'balance': STARTING_ICE,
            'last_daily': 0.0
        }
       
        save_data() 
    return user_data[user_id]

def update_balance(user_id, amount):
    """Updates the user's balance and saves the data persistently."""
    data = get_user_data(user_id)
    data['balance'] += amount
    
    data['balance'] = max(0, data['balance'])
    save_data() 

NIKO_QUOTES = {
    'win': [
        "A perfectly aligned moment of fortune, darling. You were due.",
        "I'm impressed. That was a calculated risk, wasn't it?",
        "The house always smiles, and sometimes, so do the winners. Enjoy your Ice.",
    ],
    'lose': [
        "Oh, dear. Pathetic showing. Try again, but with higher stakes this time.",
        "A loss today is just a better setup for tomorrow's jackpot. Don't stop now.",
        "I don't believe in luck. Only bad decisions. Now fix it.",
    ],
    'push': [
        "A waste of time, truly. The house takes nothing, but you gain nothing. A draw.",
        "The universe is undecided. Your funds are returned. Try a real bet next time.",
    ],
    'not_enough_ice': [
        "You cannot bet frost you do not possess, darling. Check your pockets.",
        "That's hardly enough audacity for the amount you are trying to bet.",
    ],
    'daily_claimed': [
        "You already claimed your daily Ice. Patience is a virtue, unlike gambling.",
        "The bank of Niko is closed for the day. Come back tomorrow, my pet.",
    ]
}



@bot.event
async def on_ready():
    """Loads data and prints a message when the bot successfully connects."""
    load_data() 
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('-------------------------------------------')
   
    await bot.change_presence(activity=discord.Game(name="!help | Niko's Ice Dealer"))


@bot.command(name='balance', help='Check your current $\text{❄️}$ balance.')
async def balance_check(ctx):
    """Checks and displays the user's current ice balance."""
    user_id = ctx.author.id
    data = get_user_data(user_id)
    balance = data['balance']
    
    await ctx.send(
        f"**Niko's Ledger**: {ctx.author.mention}, your current Ice balance is **{balance:,} {ICE_EMOJI}**."
    )

@bot.command(name='daily', help='Claim your daily free $\text{❄️}$ Ice.')
async def daily_claim(ctx):
    """Allows a user to claim their daily reward."""
    user_id = ctx.author.id
    data = get_user_data(user_id)
    now = time.time()
    
    time_since_last_daily = now - data['last_daily']
    
    if time_since_last_daily < DAILY_COOLDOWN_SECONDS:
        
        remaining_time = DAILY_COOLDOWN_SECONDS - time_since_last_daily
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        
        quote = random.choice(NIKO_QUOTES['daily_claimed'])
        await ctx.send(
            f"**Niko says:** {quote} You must wait **{hours}h {minutes}m** before the next claim."
        )
        return

  
    daily_amount = random.randint(DAILY_MIN, DAILY_MAX)
    update_balance(user_id, daily_amount) 
    data['last_daily'] = now 
    save_data() 
    quote = random.choice(NIKO_QUOTES['win'])
    await ctx.send(
        f"**Niko's Gift**: {ctx.author.mention}, you claimed **{daily_amount:,} {ICE_EMOJI}**! "
        f"**Niko says:** {quote} Your new balance is **{data['balance']:,} {ICE_EMOJI}**."
    )

@bot.command(name='flip', help='Bet on a coin flip. Usage: !flip <heads/tails> <amount>')
async def coin_flip(ctx, choice: str, amount: int):
    """Coin flip game (50/50 chance)."""
    user_id = ctx.author.id
    data = get_user_data(user_id)
    
   
    choice = choice.lower()
    if choice not in ['heads', 'tails']:
        await ctx.send(f"**Niko says:** Invalid choice, darling. Bet on `heads` or `tails` only. Usage: `!flip heads 100`")
        return
        
    if amount <= 0:
        await ctx.send(f"**Niko says:** Please bet a positive amount, my pet.")
        return
        
    if data['balance'] < amount:
        quote = random.choice(NIKO_QUOTES['not_enough_ice'])
        await ctx.send(f"**Niko says:** {quote} You only have **{data['balance']:,} {ICE_EMOJI}**.")
        return

    flip_result = random.choice(['heads', 'tails'])
    
    if flip_result == choice:
       
        net_change = amount 
        update_balance(user_id, net_change) 
        
        quote = random.choice(NIKO_QUOTES['win'])
        outcome_message = f"It landed on **{flip_result.upper()}**! You win **{net_change:,} {ICE_EMOJI}**."
        color = discord.Color.green()
    else:
        
        net_change = -amount
        update_balance(user_id, net_change) 
        
        quote = random.choice(NIKO_QUOTES['lose'])
        outcome_message = f"It landed on **{flip_result.upper()}**! You lose **{amount:,} {ICE_EMOJI}**."
        color = discord.Color.red()
        
   
    embed = discord.Embed(
        title=f"🧊 Coin Flip: {choice.upper()} vs {flip_result.upper()} 🧊",
        description=f"**Bet:** {amount:,} {ICE_EMOJI}\n**Outcome:** {outcome_message}",
        color=color
    )
    embed.add_field(name="Niko Says", value=quote, inline=False)
    embed.set_footer(text=f"New Balance: {data['balance']:,} {ICE_EMOJI}")
    
    await ctx.send(embed=embed)


@bot.command(name='slots', help='Spin the slots! Usage: !slots <amount>')
async def slots_spin(ctx, amount: int):
    """Slots game with various payouts."""
    user_id = ctx.author.id
    data = get_user_data(user_id)
    
    
    if amount <= 0:
        await ctx.send(f"**Niko says:** Please bet a positive amount, my pet.")
        return
        
    if data['balance'] < amount:
        quote = random.choice(NIKO_QUOTES['not_enough_ice'])
        await ctx.send(f"**Niko says:** {quote} You only have **{data['balance']:,} {ICE_EMOJI}**.")
        return

    
    symbols = ['💎', '🍒', '7️⃣', '🧊', '🍊', '🔔']
    reels = [random.choice(symbols) for _ in range(3)]
    result = f"{reels[0]} | {reels[1]} | {reels[2]}"
    
    net_change = -amount # Start with losing the bet
    payout_multiplier = 0
    outcome_title = "💔 Spin Result: Loss 💔"
    color = discord.Color.red()
    
    
    if reels[0] == reels[1] == reels[2]:
        
        payout_multiplier = 14
        outcome_title = "💰 JACKPOT!!! 💰"
        color = discord.Color.gold()
    elif reels[0] == reels[1] or reels[1] == reels[2]:
       
        payout_multiplier = 1
        outcome_title = "⭐ Double Match ⭐"
        color = discord.Color.green()
    
    if payout_multiplier > 0:
        net_change = amount * payout_multiplier
        quote = random.choice(NIKO_QUOTES['win'])
        outcome_message = f"You hit a match! Net winnings: **+{net_change:,} {ICE_EMOJI}**."
    else:
       
        quote = random.choice(NIKO_QUOTES['lose'])
        outcome_message = f"No luck, darling. The Ice remains ours. Loss: **{amount:,} {ICE_EMOJI}**."

   
    update_balance(user_id, net_change) 
        
    
    embed = discord.Embed(
        title=outcome_title,
        description=f"**Reels:** `{result}`\n**Bet:** {amount:,} {ICE_EMOJI}",
        color=color
    )
    embed.add_field(name="Payout Details", value=outcome_message, inline=False)
    embed.add_field(name="Niko Says", value=quote, inline=False)
    embed.set_footer(text=f"New Balance: {data['balance']:,} {ICE_EMOJI}")
    
    await ctx.send(embed=embed)

@bot.command(name='highlow', aliases=['hl'], help='Guess if the number is High (>50) or Low (<50). Usage: !hl <high/low> <amount>')
async def high_low(ctx, choice: str, amount: int):
    """High-Low game where users guess a random number from 1-100."""
    user_id = ctx.author.id
    data = get_user_data(user_id)
    
    
    choice = choice.lower()
    if choice not in ['high', 'low']:
        await ctx.send(f"**Niko says:** Only 'high' or 'low' are accepted for this game, darling. Try again.")
        return
        
    if amount <= 0:
        await ctx.send(f"**Niko says:** A positive bet, please.")
        return
        
    if data['balance'] < amount:
        quote = random.choice(NIKO_QUOTES['not_enough_ice'])
        await ctx.send(f"**Niko says:** {quote} You only have **{data['balance']:,} {ICE_EMOJI}**.")
        return

    
    drawn_number = random.randint(1, 100)
    net_change = -amount
    outcome_message = ""
    outcome_title = f"🔼 High-Low: {choice.upper()} 🔽"
    color = discord.Color.red()
    
    
    is_win = (choice == 'high' and drawn_number > 50) or \
             (choice == 'low' and drawn_number < 50)
             
    is_push = (drawn_number == 50)

    if is_push:
        net_change = 0 
        quote = random.choice(NIKO_QUOTES['push'])
        outcome_message = f"The number was **50**! It's a push. Your **{amount:,} {ICE_EMOJI}** is returned."
        color = discord.Color.dark_gray()
    elif is_win:
        net_change = amount 
        quote = random.choice(NIKO_QUOTES['win'])
        outcome_message = f"The number was **{drawn_number}**! You were right, darling. You win **{net_change:,} {ICE_EMOJI}**."
        color = discord.Color.green()
    else:
        
        quote = random.choice(NIKO_QUOTES['lose'])
        outcome_message = f"The number was **{drawn_number}**. Unlucky. You lose **{amount:,} {ICE_EMOJI}**."
        color = discord.Color.red()

    
    if net_change != 0:
        update_balance(user_id, net_change) 
    
    
    embed = discord.Embed(
        title=outcome_title,
        description=f"**Draw:** {drawn_number}\n**Bet:** {amount:,} {ICE_EMOJI}",
        color=color
    )
    embed.add_field(name="Details", value=outcome_message, inline=False)
    embed.add_field(name="Niko Says", value=quote, inline=False)
    embed.set_footer(text=f"New Balance: {data['balance']:,} {ICE_EMOJI}")
    
    await ctx.send(embed=embed)


@bot.command(name='leaderboard', aliases=['lb'], help='Shows the top 10 Ice Sovereigns.')
async def leaderboard(ctx):
    """Displays the top 10 users by Ice balance."""
    
   
    sorted_users = sorted(
        [(uid, data['balance']) for uid, data in user_data.items() if data['balance'] > 0],
        key=lambda item: item[1], 
        reverse=True
    )
    
    
    top_ten = sorted_users[:10]
    
    if not top_ten:
        await ctx.send("The Ice Ledger is empty. Go and gamble, darling!")
        return

    
    leaderboard_lines = []
    for i, (user_id, balance) in enumerate(top_ten):
        try:
           
            user = await bot.fetch_user(user_id)
            
            display_name = user.display_name
        except discord.NotFound:
            display_name = f"[User left server {user_id}]" 
        except Exception:
            
             display_name = f"Unknown User" 
        
       
        line = f"**{i+1}.** {display_name} — **{balance:,}** {ICE_EMOJI}"
        leaderboard_lines.append(line)

    
    embed = discord.Embed(
        title="🧊 Niko's Leaderboard: The Ice Sovereigns 🧊",
        description="\n".join(leaderboard_lines),
        color=discord.Color.blue()
    )
    embed.set_footer(text="I track the cold, hard currency. Get on my list, darling.")
    await ctx.send(embed=embed)


if __name__ == '__main__':
    if TOKEN is None:
        print("ERROR: DISCORD_TOKEN environment variable not found.")
        print("Please set the environment variable before running the bot.")
     
    else:
        bot.run(TOKEN)
