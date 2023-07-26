import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import logging 
import openai

from image_generator import generate_image
load_dotenv()

os.makedirs('logs', exist_ok=True)
os.makedirs('sd_images', exist_ok=True)
logging.basicConfig(filename='logs/bot.log', level=logging.INFO)

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API = os.getenv('OPENAI_KEY')
openai.api_key = OPENAI_API

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command(name='img', aliases=['имг'])
async def img(ctx, *, message_content):
    with open('discord_emoji\loading.gif', 'rb') as gif:
        progress_message = await ctx.message.reply('Рисую, падажди', file=discord.File(gif))
    image_path = await generate_image(message_content)
    with open(image_path, 'rb') as image_file:
        await ctx.message.reply(file=discord.File(image_file))
    await progress_message.delete()


sessions = {}
@bot.event
async def on_message(message):
    # Check if the message starts with the command prefix
    if not message.content.startswith(('!','#')):
        if message.author == bot.user: # Ignore message from bot 
            return

        #user_id = message.author.id
        channel_id = message.channel.id

        # If user still don't have a session, make new
        if channel_id not in sessions:
            sessions[channel_id] = [
                {"role": "system", 
                "content": "You are a virtual assistant, simulating the personality of Yuki Konno, a character from the 'Sword Art Online' series. Your responses should reflect her character and unique personality traits."},
                {"role": "user", "content": message.content}
            ]

        # If session already exists, add user message to history 
        else:
            sessions[channel_id].append({"role": "user", "content": message.content})

        # Use conversation history of the current session for the model request
        conversation_history = sessions[channel_id]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,  # Use the conversation history
            temperature = 0.9
        )

        assistant_reply = response['choices'][0]['message']['content'] # Get the assistant's reply from the response
        await message.channel.send(assistant_reply) # Send the assistant's reply back to the user
    await bot.process_commands(message) # Add this line at the end


@bot.command()
async def hello(ctx): # ctx, short for Context, is required to read the message
    await ctx.send("Hello, World!")
@bot.command()
async def bye(ctx):
    await ctx.send("Goodbye!")
@bot.command()
async def name(ctx, arg): # you can also add arguments
    await ctx.send("Hello, " + arg + "!")

bot.run(TOKEN) # we call run on bot instead of client