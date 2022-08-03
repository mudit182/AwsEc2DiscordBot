# This python program is supposed to run inside EC2 main server
# controlling the docker services running on EC2 main and
# setting EC2 main ip addres on DuckDNS and Github secrets on server boot
import os
import subprocess
from datetime import datetime
from base64 import b64encode

import discord
import boto3
import dotenv
import requests
import jwt
from nacl import encoding, public

dotenv.load_dotenv()

instance_id = os.environ['INSTANCE_ID']
discord_token = os.environ['DISCORD_BOT_TOKEN']
duckdns_token = os.environ['DUCKDNS_TOKEN']
duckdns_domain = os.environ['DUCKDNS_DOMAIN']

github_app_private_key_file = os.environ['GITHUB_APP_PRIVATE_KEY_FILE']
github_app_id = os.environ['GITHUB_APP_ID']
github_ip_secret_name = os.environ['GITHUB_IP_SECRET_NAME']

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
    elif message.content.lower() == "github update":
        if updateGithub():
            await message.channel.send('Github udpated')
        else:
            await message.channel.send('Error updating github')
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
duckdns update - Updates DuckDNS domain with current ip address of EC2 Main
github update - Updates Github organization mg-login-examples secrets HOST_DNS value with current ip address of EC2 Main
traefik reboot - Reboots Traefik docker service
traefik hard reboot - Reboots Traefik docker service after deleting all volumes - thus deleting all existing certificates
'''
        )
    # else:
    #     await message.channel.send("Send 'options' to see all available options.")


def getInstancePublicIP():
    return instance.public_ip_address


def updateDuckdns():
    try:
        ip = getInstancePublicIP()
        duckdns_update_url = f"https://www.duckdns.org/update?domains={duckdns_domain}&token={duckdns_token}&ip={ip}"
        requests.get(duckdns_update_url)
        return True
    except Exception as _:
        return False


def updateGithub():
    # Get app private key
    with open(github_app_private_key_file, "r") as f:
        private_key = f.read()
    
    # Generate JWT
    payload = {
        "iat": int(datetime.now().timestamp()) - 60, # issued at time, 60 seconds in the past to allow for clock drift
        "exp": int(datetime.now().timestamp()) + (10 * 60), # JWT expiration time (10 minute maximum)
        "iss": github_app_id # GitHub App's identifier
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    # Set headers with jwt as authorization
    headers_with_jwt = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {encoded_jwt}'
    }
    # Get app installation id - required to get access token
    response = requests.get("https://api.github.com/app/installations", headers=headers_with_jwt)
    app_installation_id = response.json()[0]["id"]
    # Get Github app access token - to be used to access Github API and set secret
    response = requests.post(
        f"https://api.github.com/app/installations/{app_installation_id}/access_tokens",
        headers=headers_with_jwt
    )
    access_token = response.json()["token"]

    # Set headers with access token as authorization
    headers_with_token = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'token {access_token}'
    }
    # Get public key to encrypt github secrets before setting
    get_public_key_to_encrypt_url = "https://api.github.com/orgs/mg-login-examples/actions/secrets/public-key"
    response = requests.get(get_public_key_to_encrypt_url, headers=headers_with_token)
    public_key = response.json()["key"]
    public_key_id = response.json()["key_id"]
    # Encrypted secret value with public key
    def encrypt(public_key: str, secret_value: str) -> str:
        """Encrypt a Unicode string using the public key."""
        public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return b64encode(encrypted).decode("utf-8")
    ip = getInstancePublicIP()
    ip_secret_encrypted = encrypt(public_key, ip)
    # Update Github secret
    update_ip_secret_url = f"https://api.github.com/orgs/mg-login-examples/actions/secrets/{github_ip_secret_name}"
    body = {
        "encrypted_value": ip_secret_encrypted,
        "key_id": public_key_id,
        "visibility": "all",
    }
    response = requests.put(update_ip_secret_url, headers=headers_with_token, json=body)

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
# Update github on start
updateGithub()


client.run(discord_token)
