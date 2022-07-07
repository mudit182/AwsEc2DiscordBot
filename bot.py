import os
import discord
import boto3
import dotenv

dotenv.load_dotenv()

instance_id = os.environ['INSTANCE_ID']
discord_token = os.environ['DISCORD_BOT_TOKEN']

client = discord.Client()
ec2 = boto3.resource('ec2')
instance = ec2.Instance(instance_id)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "start":
        if turnOnInstance():
            await message.channel.send('AWS Instance starting')
        else:
            await message.channel.send('Error starting AWS Instance')
    elif message.content.lower() == "stop":
        if turnOffInstance():
            await message.channel.send('AWS Instance stopping')
        else:
            await message.channel.send('Error stopping AWS Instance')
    elif message.content.lower() == "reboot":
        if rebootInstance():
            await message.channel.send('AWS Instance rebooting')
        else:
            await message.channel.send('Error rebooting AWS Instance')
    elif message.content.lower() == "state":
        if getInstanceState():
            await message.channel.send('AWS Instance state is: ' + getInstanceState())
    elif message.content.lower() == "ip":
        if getInstancePublicIP():
            await message.channel.send(getInstancePublicIP())
    elif message.content.lower() == "options":
        await message.channel.send(
'''
start - Starts EC2
stop - Stops EC2
state - Returns EC2 current state
reboot - Reboots EC2
'''
        )
    else:
        await message.channel.send("Send 'options' to see all available options.")

def turnOffInstance():
    try:
        instance.stop()
        return True
    except Exception as _:
        return False

def turnOnInstance():
    try:
        instance.start()
        return True
    except Exception as _:
        return False

def getInstanceState():
        return instance.state['Name']

def getInstancePublicIP():
    return instance.public_ip_address

def rebootInstance():
    try:
        instance.reboot()
        return True
    except Exception as _:
        return False

client.run(discord_token)
