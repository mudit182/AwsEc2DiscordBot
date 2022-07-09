import os
import subprocess

import discord
import boto3
import dotenv
import requests

dotenv.load_dotenv()

instance_id = os.environ['INSTANCE_ID']
discord_token = os.environ['DISCORD_BOT_TOKEN']
duckdns_token = os.environ['DUCKDNS_TOKEN']
duckdns_domain = os.environ['DUCKDNS_DOMAIN']
traefik_reboot_script_path = os.environ['TRAEFIK_REBOOT_SCRIPT_PATH']
traefik_hard_reboot_script_path = os.environ['TRAEFIK_HARD_REBOOT_SCRIPT_PATH']
traefik_dir = os.environ['TRAEFIK_DIR']

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

    if message.content.lower() == "duckdns update":
        if updateDuckdns():
            await message.channel.send('Duckdns udpated')
        else:
            await message.channel.send('Error updating duckdns')
    elif message.content.lower() == "traefik reboot":
        if rebootTraefik():
            await message.channel.send('Traefik docker service rebooted')
        else:
            await message.channel.send('Error rebooting traefik docker service')
    elif message.content.lower() == "traefik hard reboot":
        if hardRebootTraefik():
            await message.channel.send('Traefik docker service hard rebooted')
        else:
            await message.channel.send('Error hard rebooting traefik docker service')
    elif message.content.lower() == "options":
        await message.channel.send(
'''
duckdns update - Updates DuckDNS domain to track ip address of EC2 Main
traefik reboot - Reboots Traefik docker service
traefik hard reboot - Reboots Traefik docker service after deleting all volumes - thus deleting all existing certificates
'''
        )
    # else:
    #     await message.channel.send("Send 'options' to see all available options.")

def updateDuckdns():
    try:
        ip = getInstancePublicIP()
        duckdns_update_url = f"https://www.duckdns.org/update?domains={duckdns_domain}&token={duckdns_token}&ip={ip}"
        requests.get(duckdns_update_url)
        return True
    except Exception as _:
        return False

def getInstancePublicIP():
    return instance.public_ip_address

def rebootTraefik():
    try:
        process = subprocess.Popen(f"{traefik_reboot_script_path}", shell=True, stdout=subprocess.PIPE, cwd=traefik_dir)
        process.wait()
        if process.returncode == 0:
            return True
        else:
            return False
    except Exception as _:
        return False

def hardRebootTraefik():
    try:
        process = subprocess.Popen(f"{traefik_hard_reboot_script_path}", shell=True, stdout=subprocess.PIPE, cwd=traefik_dir)
        process.wait()
        if process.returncode == 0:
            return True
        else:
            return False
    except Exception as _:
        return False


# Update duckdns on start
updateDuckdns()

client.run(discord_token)
