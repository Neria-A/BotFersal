# BotFersal 🤖💳
Say hello to **BotFersal**.

Telegram bot that connects to the 10bis website via API to fetch your personal Shufersal vouchers.
It then saves the barcode ID of each voucher in MongoDB and generates a voucher barcode when needed.
Use this bot to easily manage your vouchers and redeem them quickly! 🚀

# Updating appSettings.py
To activate the bot, you'll need to change four values in the "appSettings.py" file in the BotFersal repository:

**botToken**- This is the Telegram API token for your bot. You can obtain this token from the BotFather bot on Telegram.

**mongo_connection_string**- This is the MongoDb connection string.

**ten_bis_mail**- This is your 10bis username (i.e., the email address associated with your 10bis account).

**user_name**-  This is your Telegram user name starts with @.

## Make sure to update these values with your own information before running the bot.

## _botToken_
1. Open Telegram and search for the BotFather bot.
2. Start a conversation with the BotFather bot by sending the message "/start".
3. Send the BotFather bot the command "/newbot" to create a new bot.
4. Follow the prompts to choose a name and username for your new bot. Once you've chosen a username that's not already taken, the BotFather will provide you with an API token for your bot.
5. Copy the API token and paste it into the TELEGRAM_TOKEN variable in the "appSettings.py" file in the BotFersal repository.

## _mongo_connection_string_
1. Go to the [MongoDB](https://www.mongodb.com/) website and click on the “Try Free” button in the top right corner of the homepage.
2. Fill in your details to create a new account, including your name, email address, and password. You can also sign up with your Google or GitHub account if you prefer.
3. After signing up, you’ll be directed to the dashboard. From there, click on the “Create a New Project” button to create a new project.
4. Give your project a name and click on the “Create Project” button.
5. Once your project is created, click on the “Build a Cluster” button to create a new cluster.
6. Choose the “Shared” option for the free tier and click on the “Create Cluster” button.
7. Wait for your cluster to be created. This may take a few minutes.
8. Once your cluster is created, click on the “Connect” button.
9. Select “Connect Your Application” to get the connection string.
10. Choose your driver and version, and copy the connection string to use in your application.


