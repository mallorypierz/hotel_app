"""Backend environment configuration, loaded once when the process starts."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env')
GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY', '').strip()

# Chatbot settings stay backend-only. Invalid settings are handled without fallback.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini-2025-04-14').strip()
OPENAI_TIMEOUT_SECONDS = os.getenv('OPENAI_TIMEOUT_SECONDS', '20').strip()
OPENAI_MAX_OUTPUT_TOKENS = os.getenv('OPENAI_MAX_OUTPUT_TOKENS', '1800').strip()
