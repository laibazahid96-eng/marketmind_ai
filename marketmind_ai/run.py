from dotenv import load_dotenv
load_dotenv()  # Loads the OPENAI_API_KEY from .env

from src.llm import ReliableLLMClient
from src.tools import ToolDispatcher
from src.agents import AutonomousResearchLoop

llm = ReliableLLMClient()
dispatcher = ToolDispatcher()
agent = AutonomousResearchLoop(llm_client=llm, dispatcher=dispatcher)

print("MarketMind Agent initialized and ready.")