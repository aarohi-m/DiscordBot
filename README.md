# DiscordBot
# niko

<img width="1406" height="454" alt="Screenshot 2025-09-28 160127" src="https://github.com/user-attachments/assets/d0b3c22e-b768-47d7-aa38-5c57678ffd11" />

<img width="572" height="503" alt="Screenshot 2025-09-28 160158" src="https://github.com/user-attachments/assets/6e05df85-dbb4-462a-90e3-29134d7f78bc" />



# Architectural Foundation: Event-Driven Model
Client-Server and Abstraction
Niko operates on a standard Client-Server Model.  Python script is the client, and the Discord platform is the server. Communication is managed by the discord.py framework.

Discord API (Server): Handles all messages, user data, and server state using REST (for setup, like fetching a channel list) and persistent WebSockets (for real-time events, like receiving a message).

discord.py (Abstraction Layer): This library handles the complex, low-level networking. Instead of manually crafting HTTP requests and managing WebSocket connection failures, the library translates raw data into easily manipulable Python objects.

Event-Driven Architecture (EDA): The entire bot runs on an EDA.  the bot waits for Discord to push an event. The @bot.command decorators serve as event listeners that fire a specific function only when a recognized command is received.


# Concurrency Model: Asynchronous I/O
The use of the async and await keywords is perhaps the most crucial technical aspect of the bot's performance.

Non-Blocking I/O
The key requirement for a scalable bot is non-blocking Input/Output (I/O). When your bot sends a message to Discord (I/O), it takes a few milliseconds for the server to process it and send back a confirmation.


By using Asynchronous I/O, when the line await ctx.send() is hit, the bot's Event Loop pauses the current function (coin_flip) and immediately moves on to processing the next waiting command (say, a different user's !slots request). When the Discord API response returns, the Event Loop jumps back and finishes the original coin_flip task.

#  Data Layer: Persistence and State Management
Since Discord bots are designed to be stateless, we must use a mechanism for state persistence.

Model: The core data model is a key-value store (a Python dictionary) mapping the user's integer Discord ID to their account data:
JSON Serialization: We use the json module to perform serialization (converting the Python dictionary object to a string format for storage) and deserialization (converting the string back into a usable Python object upon startup).

Integrity: The save_data() function is called immediately after any successful modification (win, loss, daily claim). This ensures data integrity by enforcing frequent writes to disk, minimizing the risk of losing recent changes during a crash.

# COMMANDS FOR USE:
Command       Alias    Description                                                         Usage Example
!balance              Check your current Ice (❄R◯) balance.                               !balance
!daily                Claim your daily free Ice reward (24-hour cooldown).                  !daily
!flip                 Bet on a coin flip (Heads or Tails).                                  !flip heads 500
!slots                Spin the slots machine for various payouts.                           !slots 1000
!highlow       !hl    Guess if a random number (1-100) will be High (>50) or Low (<50).     !hl high 250
!leaderboard   !lb    Shows the top 10 richest Ice Sovereigns on the server.                !leaderboard


# Invite to server:
https://discord.com/oauth2/authorize?client_id=1421763341243777117&permissions=8&integration_type=0&scope=bot




