# AWS EC2 Controller Discord Bot
This is a fork from https://github.com/leobeosab/AwsEc2DiscordBot

## Tools Used
* Python 3 and pip3 : ```install python3 
install python3-pip```
* AWS CLI : 
* AWS BOTO library : ``` pip3 install boto3 ```
* Discord Bot library : ``` pip3 install discord ```

## Usage | Installation
1. Install and setup the required tools above
2. Setup AWS CLI with ``` pip3 awscli ```
3. Set AWS IAM credentials with ```aws configure```
    *You will need to add an IAM User in AWS Console with permissions to access your EC2.
3. Go to Discord's developer site and setup a bot [here](https://discordapp.com/developers)
4. Clone this repo into the home location for your user.
5. Create a file named .env and enter the variables for your Discord token and your AWS instance ID. Doing this will help protect your secrets.
```instance_id='INSERTID discord_key='INSERTKEY'```
6. Make your file executable ```chmod +x bot.py```
7. Now run your bot! python3 bot.py

#### All Environment variables
INSTANCE_ID=
DISCORD_BOT_TOKEN=
DUCKDNS_TOKEN=
DUCKDNS_DOMAIN=
TRAEFIK_REBOOT_SCRIPT_PATH=

To use systemd to schedule your bot to run enter this in the command line. 
```[Unit]
Description=DiscordBot
After=multi-user.target

[Service]
Type=simple
Restart=always
User=ec2-user
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/bot.py

[Install]
WantedBy=multi-user.target```