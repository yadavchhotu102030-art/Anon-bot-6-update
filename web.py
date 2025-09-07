import os
import subprocess
from flask import Flask

# Start the Telegram bot as a background process
subprocess.Popen(["python", "bot.py"])

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Required by PaaS
    app.run(host="0.0.0.0", port=port)
