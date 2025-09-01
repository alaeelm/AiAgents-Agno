# WhatsApp Todoist Assistant 🤖📱

An intelligent personal assistant that connects WhatsApp with Todoist using Google Gemini AI. Manage your tasks naturally through WhatsApp conversations with real-time data and contextual responses.

## ✨ Features

- 🗣️ **Natural Language Processing** - Communicate with your to-do list in plain language
- ⏰ **Real-time Task Management** - Add, view, and manage Todoist tasks through WhatsApp
- 🌍 **Timezone Aware** - Automatically handles dates and times for Africa/Casablanca timezone
- 🎯 **Context-Aware Responses** - Understands greetings, time-based queries, and task priorities
- 📱 **WhatsApp Integration** - Works directly in your favorite messaging app
- 🔄 **Background Processing** - Asynchronous message handling for optimal performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WhatsApp      │───▶│  FastAPI Server  │───▶│  Gemini Agent   │
│   Messages      │    │  (Webhooks)      │    │  (AI Logic)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  WhatsApp API    │    │  Todoist API    │
                       │  (Meta Graph)    │    │  (Tasks CRUD)   │
                       └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- WhatsApp Business API access
- Google Gemini API key
- Todoist API token
- Public URL for webhooks (ngrok, Railway, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-todoist-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file:
   ```env
   # Google Gemini
   GOOGLE_API_KEY=your_google_api_key

   # Todoist
   TODOIST_API_KEY=your_todoist_api_key

   # WhatsApp Business API
   VERSION=v23.0
   PHONE_NUMBER_ID=your_phone_number_id
   WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
   RECIPIENT_PHONE_NUMBER=your_phone_number
   VERIFY_TOKEN=your_webhook_verify_token
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Configure webhook**
   Set your webhook URL in Meta Developer Console:
   ```
   https://your-domain.com/webhook
   ```

## 📋 API Keys Setup

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### Todoist API
1. Go to [Todoist App Console](https://todoist.com/app/settings/integrations)
2. Create a new app and get your API token
3. Add it to your `.env` file

### WhatsApp Business API
1. Create a [Meta Developer Account](https://developers.facebook.com/)
2. Set up WhatsApp Business API
3. Get your access token, phone number ID, and set up webhooks
4. Add credentials to your `.env` file

## 💬 Usage Examples

### Daily Greetings
```
👤 User: Good evening assistant
🤖 Bot: 🌙 Good evening! You have 2 tasks today:
       📝 Submit report by 6 PM
       📞 Call John at 8 PM
```

### Adding Tasks
```
👤 User: Add task: Buy groceries tomorrow at 5 PM
🤖 Bot: ✅ Added: 🛒 Buy groceries tomorrow at 5 PM
```

### Checking Current Tasks
```
👤 User: What do I have now?
🤖 Bot: ✅ No tasks this hour. You're clear!
```

### Priority Tasks
```
👤 User: Any important tasks today?
🤖 Bot: ⚠️ High priority: 📊 Submit budget report by 6 PM
```

## 📂 Project Structure

```
├── main.py                 # FastAPI server and webhook endpoints
├── agent_service.py        # Gemini AI agent configuration and tools
├── whatsapp_utils.py       # WhatsApp API utilities
├── .env                    # Environment variables (create this)
└── README.md              # This file
```

## 🔧 Core Components

### 1. **main.py** - FastAPI Server
- Webhook verification and handling
- Asynchronous message processing
- Health check and test endpoints

### 2. **agent_service.py** - AI Agent
- Google Gemini model configuration
- Detailed instructions for natural language understanding
- Tool definitions for Todoist integration
- Real-time datetime handling

### 3. **whatsapp_utils.py** - WhatsApp Integration
- Message parsing and validation
- Response formatting and sending
- Error handling and logging

## 🛠️ Available Tools

The AI agent has access to three main tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_current_datetime` | Get real-time date/time | None |
| `get_tasks` | Fetch all Todoist tasks | None |
| `add_task` | Create new task | `content`, `due_datetime` (optional) |

## 🚀 Deployment

### Using Railway
1. Connect your GitHub repository
2. Add environment variables in Railway dashboard
3. Deploy automatically

### Using Render
1. Create new web service
2. Connect repository
3. Add environment variables
4. Deploy

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🔍 Testing

### Test WhatsApp Connection
```bash
curl http://localhost:8000/test
```

### Send Test Message
```bash
curl http://localhost:8000/send_message
```

### Manual Agent Test
```python
from agent_service import get_response
print(get_response("what tasks do I have today?"))
```

## ⚠️ Important Notes

- **Always use real-time data** - The agent never guesses dates or times
- **Webhook security** - Verify tokens to prevent unauthorized access
- **Rate limiting** - Be aware of API limits for all services
- **Error handling** - All API calls include proper exception handling
- **Background processing** - Messages are processed asynchronously

## 🐛 Troubleshooting

### Common Issues

**Webhook verification fails**
- Check your `VERIFY_TOKEN` matches Meta Developer Console
- Ensure your server is publicly accessible

**Tasks not syncing**
- Verify `TODOIST_API_KEY` is correct
- Check API rate limits

**AI responses seem off**
- Ensure `GOOGLE_API_KEY` is valid
- Check if datetime API is accessible

**WhatsApp messages not sending**
- Verify `WHATSAPP_ACCESS_TOKEN` and `PHONE_NUMBER_ID`
- Check webhook URL configuration

### Logs
The application logs all HTTP responses and errors. Check console output for debugging information.

## 🔄 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [Todoist API](https://developer.todoist.com/) for task management
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp) for messaging
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Agno Framework](https://github.com/agno-ai/agno) for AI agent structure

