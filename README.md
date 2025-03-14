# Telegram_bot
Project: AI-Powered Telegram Chatbot  Features: ✅ User Registration (MongoDB) ✅ Gemini AI Chatbot ✅ AI-Powered Web Search ⚠ Image/File Analysis (Known Issues)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
Step 1: **Create a New Bot Using BotFather**
Open Telegram and search for BotFather.

BotFather is the official Telegram bot used to create and manage other bots.
Start a chat with BotFather:

Click the “Start” button to begin interacting with BotFather.
Create a New Bot:

Type /newbot and send the message.
BotFather will ask you for a name for your bot. This is the name that will be visible to users.
After that, BotFather will ask for a username for your bot. The username must be unique and end with bot (e.g., mynewcoolbot).
Get Your Bot Token:XXXXXXXXXXXX

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 **MongoDB Atlas (Cloud Setup)**
Create an Account:

Go to MongoDB Atlas and create an account if you don’t already have one.
Create a New Cluster:

After logging in, click on "Build a Cluster" to create a free cluster.
Select the cloud provider, region, and cluster tier. The free tier is usually sufficient.
Set Up Database Access:

Go to Database Access in the Atlas dashboard.
Create a new user with a username and password. You'll use these credentials to access your database.
Create a Database:

Go to Clusters and click on Collections.
Click on Create Database. Choose a name for your database (e.g., TelegramBotDB) and a collection (e.g., users).
Get Connection String:

Go to the Clusters tab and click Connect.
Choose Connect your application.
Copy the connection string and replace the <password> placeholder with your MongoDB password and <dbname> with the name of your database (e.g., TelegramBotDB).
Example connection string:
mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**API KEY USES**
GEMINI_API_KEY  (USER INTERATIONS)
SERP_API_KEY    (WEB SEARCH)

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

![image](https://github.com/user-attachments/assets/1ee0a2c0-5be1-47ca-b667-336fe1e22bec)





--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
