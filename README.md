# AWS EC2 Controller Discord Bot
This is a fork from https://github.com/leobeosab/AwsEc2DiscordBot

## Tools Used
* Python 3 and pip3
* AWS CLI
* AWS BOTO library
* Discord Bot library

## Usage | Installation
1. Install and setup the required tools above
2. Setup AWS CLI with ``` pip3 awscli ```
3. Set AWS IAM credentials with ```aws configure```
    *You will need to add an IAM User in AWS Console with permissions to access your EC2.
3. Go to Discord's developer site and setup a bot [here](https://discordapp.com/developers)
4. Clone this repo into the home location for your user.
5. Create a file named .env and enter the variables for your Discord token and your AWS instance ID. Doing this will help protect your secrets.
```instance_id='INSERTID discord_key='INSERTKEY'```
    Add .pem file where required
6. Make your file executable ```chmod +x bot.py```
7. Now run your bot! python3 bot.py

#### All Environment variables
INSTANCE_ID=
DISCORD_BOT_TOKEN=
DUCKDNS_TOKEN=
DUCKDNS_DOMAIN=
GITHUB_APP_PRIVATE_KEY_FILE=
GITHUB_APP_ID=
GITHUB_IP_SECRET_NAME=
TRAEFIK_REBOOT_SCRIPT_PATH=
TRAEFIK_HARD_REBOOT_SCRIPT_PATH=
TRAEFIK_DIR=


### Add it as a linux systemd service

1. Navigate to /etc/systemd/system and modify your service file if required
2. Create your custom service file with the name: <my-service-name>.service
3. Paste the content below inside the file. Modify the python path and file path accordingly
```[Unit]
Description=DiscordBot
After=multi-user.target

[Service]
Type=simple
Restart=always
User=ec2-user
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/bot.py

[Install]
WantedBy=multi-user.target
```

4. Load the newly created service file: `sudo systemctl daemon-reload`
5. start systemd service: `sudo systemctl start <my-service-name>`
6. To have the service start on server boot: `sudo systemctl enable <my-service-name>`


### Update existing systemd service
If a systemd service already exists, to update the changes:
1. Navigate to /etc/systemd/system and modify your service file if required
2. Run `sudo systemctl daemon-reload` to use the latest changed systemd service file
3. Restart your service `sudo systemctl restart <my-service-name>`
