# WhatsApp Business Backend API

FastAPI backend for the WhatsApp Business Dashboard.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment file:
```bash
copy .env.example .env
```

3. Update `.env` with your WhatsApp Business API credentials

## Running the Server

Development mode (with auto-reload):
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 4000
```

The API will be available at: http://localhost:4000

API Documentation (Swagger UI): http://localhost:4000/docs
Alternative docs (ReDoc): http://localhost:4000/redoc

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/messages` - Get all messages
- `GET /api/messages/{id}` - Get specific message
- `POST /api/messages` - Send a new message
- `GET /api/contacts` - Get all contacts
- `GET /api/contacts/{id}` - Get specific contact
- `GET /api/stats` - Get dashboard statistics

## Integration with WhatsApp Business API

This backend is ready to be integrated with the official WhatsApp Business API. Update the message sending endpoint to use the WhatsApp Graph API when you have your credentials configured.

## Twilio WhatsApp Sandbox Webhook Setup (Local Development)

For local development and testing with Twilio WhatsApp Sandbox, you need to expose your local backend using ngrok.

### Step 1: Install ngrok

Download and install ngrok from: https://ngrok.com/download

### Step 2: Start your backend server

```bash
python main.py
```

The server will run on `http://localhost:4000`

### Step 3: Start ngrok tunnel

In a new terminal, run:

```bash
ngrok http 4000
```

You'll see output like:

```
Forwarding    https://abcd1234.ngrok-free.app -> http://localhost:4000
```

Copy the HTTPS URL (e.g., `https://abcd1234.ngrok-free.app`)

### Step 4: Configure Twilio WhatsApp Sandbox

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to: **Messaging → Try it out → Send a WhatsApp message**
3. Click on **WhatsApp Sandbox Settings**
4. In the "When a message comes in" field, enter:
   ```
   https://abcd1234.ngrok-free.app/webhook/whatsapp
   ```
   (Replace `abcd1234` with your actual ngrok URL)
5. Save the configuration

### Step 5: Test the webhook

1. Send a WhatsApp message to your Twilio Sandbox number (starts with +1 415...)
2. Check your backend logs to see the incoming message
3. You should receive a reply: "Welcome 👋\nYour WhatsApp ordering bot is live."

### Important Notes

- **Twilio cannot call localhost directly** - You must use ngrok (or similar tunneling service)
- The ngrok URL changes each time you restart ngrok (unless you have a paid plan)
- For production, use a proper domain with HTTPS instead of ngrok
- The webhook endpoint is available at: `POST /webhook/whatsapp`
- The endpoint accepts `application/x-www-form-urlencoded` data from Twilio
- It returns TwiML XML response for WhatsApp messages

### Webhook Endpoint Details

- **URL**: `/webhook/whatsapp`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Response**: TwiML XML
- **Fields Read**: `From` (sender number), `Body` (message text)
- **Logs**: Both fields are logged for debugging

