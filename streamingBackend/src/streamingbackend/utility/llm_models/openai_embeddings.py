from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from streamingbackend.rag.config import get_repo_root

load_dotenv(get_repo_root() / ".env")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
