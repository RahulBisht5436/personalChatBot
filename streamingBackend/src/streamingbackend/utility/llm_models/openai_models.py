from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from streamingbackend.rag.config import get_repo_root

load_dotenv(get_repo_root() / ".env")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
