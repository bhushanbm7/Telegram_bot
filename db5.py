from pymongo import MongoClient
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import datetime
import requests  # For making HTTP requests to the web search API
import os  # For handling file paths

# MongoDB Connection
client = MongoClient("mongodb+srv://hemantkumarnivruttibharambe:Hemant87677@cluster0.14pug.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["TelegramBotDB"]
users = db["users"]
chat_history = db["chat_history"]
file_metadata = db["file_metadata"]  # Collection for storing file metadata

# Gemini API Key Configuration
GEN_API_KEY = "AIzaSyDfHHLZdrXa4ZO_1MGIqnGOm8QJusHnzjc"  # Replace with your Gemini API key
genai.configure(api_key=GEN_API_KEY)

# Web Search API Configuration (e.g., SerpAPI or Google Custom Search API)
WEB_SEARCH_API_KEY = "31f32700ffc4248bc46d7feb2e8e8387a536790e478e849ab4d33855d335a331"  # Replace with your web search API key
WEB_SEARCH_API_URL = "https://serpapi.com/search"  # Example: SerpAPI endpoint


# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    existing_user = users.find_one({"chat_id": user.id})

    if existing_user:
        await update.message.reply_text(f"👋 Welcome back, {user.first_name}!")
    else:
        keyboard = [[KeyboardButton("📱 Share Contact", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Welcome! Please share your phone number using the button below.",
                                        reply_markup=reply_markup)


# Handle Contact Sharing
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    contact = update.message.contact

    if contact.user_id != user.id:
        await update.message.reply_text("❌ Please share your own contact number.")
        return

    # Save user data to MongoDB
    user_data = {
        "first_name": user.first_name,
        "username": user.username,
        "chat_id": user.id,
        "phone_number": contact.phone_number
    }

    users.update_one({"chat_id": user.id}, {"$set": user_data}, upsert=True)
    await update.message.reply_text(f"✅ Thank you, {user.first_name}! Your phone number has been saved.")


# Gemini Chat Function
async def gemini_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.message.from_user
    chat_id = user.id

    try:
        # Fetch AI Response
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_message)

        # Extract text response properly
        if response.candidates and response.candidates[0].content.parts:
            bot_reply = response.candidates[0].content.parts[0].text.strip()
        else:
            bot_reply = "⚠️ Sorry, I couldn't generate a response."

        # Add emojis based on the response type
        if "?" in bot_reply:
            bot_reply += " 🤔"
        elif "!" in bot_reply:
            bot_reply += " 🎉"
        else:
            bot_reply += " 😊"

        # Provide auto-follow-up suggestions based on the user's query
        auto_follow_up = ""
        if "weather" in user_message.lower():
            auto_follow_up = "🌦️ Want to know the weather in your city? Just type 'weather' and your city name!"
        elif "news" in user_message.lower():
            auto_follow_up = "📰 Interested in the latest news? Try asking about world or tech news!"
        elif "music" in user_message.lower():
            auto_follow_up = "🎶 Looking for new music recommendations? Just ask for the latest hits!"

        if auto_follow_up:
            bot_reply += f"\n\n👉 {auto_follow_up}"

        # Store chat history in MongoDB
        chat_data = {
            "chat_id": chat_id,
            "username": user.username,
            "first_name": user.first_name,
            "user_message": user_message,
            "bot_response": bot_reply,
            "timestamp": datetime.datetime.now(datetime.UTC)
        }
        chat_history.insert_one(chat_data)

        # Send AI Response with emojis and suggestions
        await update.message.reply_text(bot_reply)

    except Exception as e:
        await update.message.reply_text("⚠️ Sorry, an error occurred while processing your request.")
        print(f"Error: {e}")


# Web Search Function
async def web_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = user.id
    query = " ".join(context.args)  # Extract the search query from the command

    if not query:
        await update.message.reply_text("Please provide a search query. Usage: /websearch <query>")
        return

    try:
        # Perform a web search using the API
        params = {
            "q": query,
            "api_key": WEB_SEARCH_API_KEY  # Add other required parameters for the API
        }
        response = requests.get(WEB_SEARCH_API_URL, params=params)
        search_results = response.json()

        # Extract top search results
        top_results = search_results.get("organic_results", [])[:5]  # Get top 5 results
        if not top_results:
            await update.message.reply_text("⚠️ No results found for your query.")
            return

        # Format the results for the user
        result_summary = f"🔍 Web Search Results for '{query}':\n\n"
        for i, result in enumerate(top_results, 1):
            result_summary += f"{i}. {result['title']}\n{result['link']}\n\n"

        # Use Gemini to summarize the results
        model = genai.GenerativeModel("gemini-pro")
        summary_prompt = f"Summarize the following web search results in 2-3 sentences:\n\n{result_summary}"
        summary_response = model.generate_content(summary_prompt)

        if summary_response.candidates and summary_response.candidates[0].content.parts:
            summary = summary_response.candidates[0].content.parts[0].text.strip()
        else:
            summary = "⚠️ Sorry, I couldn't generate a summary."

        # Send the summary and top links to the user
        await update.message.reply_text(f"📝 Summary:\n{summary}\n\n🔗 Top Links:\n{result_summary}")

    except Exception as e:
        await update.message.reply_text("⚠️ Sorry, an error occurred while performing the web search.")
        print(f"Error: {e}")


# Image/File Analysis Function
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = user.id

    # Check if the message contains a document or photo
    if update.message.document:
        file = await update.message.document.get_file()
        file_extension = os.path.splitext(update.message.document.file_name)[1].lower()
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()  # Get the highest resolution photo
        file_extension = ".jpg"
    else:
        await update.message.reply_text("⚠️ Unsupported file type. Please upload an image or document.")
        return

    try:
        # Download the file
        file_path = f"downloads/{file.file_id}{file_extension}"
        await file.download_to_drive(file_path)

        # Analyze the file using Gemini
        model = genai.GenerativeModel("gemini-pro")
        with open(file_path, "rb") as f:
            file_content = f.read()

        response = model.generate_content(
            f"Describe the content of this file: {file_content}"
        )

        if response.candidates and response.candidates[0].content.parts:
            description = response.candidates[0].content.parts[0].text.strip()
        else:
            description = "⚠️ Sorry, I couldn't analyze the file."

        # Save file metadata in MongoDB
        file_data = {
            "chat_id": chat_id,
            "username": user.username,
            "first_name": user.first_name,
            "file_id": file.file_id,
            "file_name": update.message.document.file_name if update.message.document else "photo.jpg",
            "file_extension": file_extension,
            "description": description,
            "timestamp": datetime.datetime.now(datetime.UTC)
        }
        file_metadata.insert_one(file_data)

        # Send the analysis to the user
        await update.message.reply_text(f"📄 File Analysis:\n{description}")

        # Clean up the downloaded file
        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text("⚠️ Sorry, an error occurred while analyzing the file.")
        print(f"Error: {e}")


# Main Function to Run the Bot
if __name__ == "__main__":
    bot_token = "7899629472:AAFQR3ZQctUCf1th3bMv8zpPTACIdPSs-Vg"  # Replace with your Telegram Bot token
    app = ApplicationBuilder().token(bot_token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gemini_chat))  # AI Chat
    app.add_handler(CommandHandler("websearch", web_search))  # Web Search
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))  # Image/File Analysis

    # Create the downloads directory if it doesn't exist
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # Start the bot
    print("🤖 Bot is running...")
    app.run_polling()
