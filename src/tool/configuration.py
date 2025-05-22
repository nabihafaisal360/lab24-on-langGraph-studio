from langchain.chat_models import init_chat_model
from react_agent.tools import tools
from dotenv import load_dotenv
load_dotenv()

#model 

llm = init_chat_model("google_genai:gemini-2.0-flash")