# Anonymous Telegram Bot (Updated)

## 🚀 Features
- Anonymous random chat matching
- Clean UI with buttons and emojis
- Spectator group mirroring for admins
- Error handling: ignores minor errors, reports critical ones
- `/getid` command to get group IDs
- 🆕 Logs new users' names, usernames, and IDs when they join
- 🆕 Notifies spectator group when chats end

## 🛠 Deployment Instructions

### Railway
1. Push code to GitHub.
2. Create a new project in Railway, link repo.
3. Set environment variables:
   - BOT_TOKEN
   - ADMIN_IDS (comma-separated IDs)
   - SPECTATOR_GROUP_ID (optional)
4. Start command: `python web.py`

### Heroku
1. Push code to GitHub.
2. Create new Heroku app, link repo.
3. Add environment variables in app settings.
4. Heroku will detect `Procfile`:
   ```
   worker: python web.py
   ```
5. Deploy app.
