export const widgetConfig = {
  assistantName: "Rahul AI",
  ownerName: "Rahul Bisht",
  greeting: "Hi! Chat with Rahul AI",
  greetingSent: "Message sent to Rahul 😊",
  greetingSentSubtext: "He'll get back to you as soon as possible!",
  subtitle: "Portfolio Assistant",
  welcomeTitle: "Ask me about Rahul",
  welcomeText:
    "I can help with education, skills, projects, and experience. RAG will make this smarter soon.",
  placeholder: "Ask about education, skills, projects...",
  suggestedPrompts: [
    "What have you studied?",
    "Tell me about your B.Tech background",
    "What skills do you have?",
    "I'd like to hire Rahul",
  ],
  highlightStats: [
    { label: "B.Tech", detail: "Computer Science" },
    { label: "Full Stack", detail: "React & Python" },
    { label: "AI / ML", detail: "LangGraph" },
    { label: "Projects", detail: "Portfolio apps" },
  ],
} as const;
