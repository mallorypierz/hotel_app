"""Backend environment configuration, loaded once when the process starts."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env')
GEOAPIFY_API_KEY = os.getenv('GEOAPIFY_API_KEY', '').strip()
