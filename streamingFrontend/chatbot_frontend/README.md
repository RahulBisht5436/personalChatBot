# Chatbot Frontend

Next.js frontend for the Streaming chatbot, including a floating widget and embeddable script.

## Setup

```powershell
cd Streaming/streamingFrontend/chatbot_frontend
npm install
copy .env.local.example .env.local
```

## Run

Backend (terminal 1):

```powershell
cd Streaming/streamingBackend
uv run serve
```

Frontend (terminal 2):

```powershell
cd Streaming/streamingFrontend/chatbot_frontend
npm run dev
```

Open:

- Main site with floating widget: http://localhost:3000
- Embed widget page: http://localhost:3000/embed/chat
- Third-party embed demo: http://localhost:3000/embed-demo.html

## Embed on any website

```html
<script
  src="https://your-frontend-domain.com/embed.js"
  data-widget-origin="https://your-frontend-domain.com"
  data-api-url="https://your-api-domain.com"
  async
></script>
```

## Environment

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL |
