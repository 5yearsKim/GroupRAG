import os
from dotenv import load_dotenv
load_dotenv()

STAGE: str = os.getenv('STAGE', 'dev')

QDRANT_URL: str = os.getenv('QDRANT_URL', 'http://localhost:6333')

QDRANT_NAMESPACE = 'gossip_prod' if STAGE == 'prod' else 'gossip_dev'

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

PORT= 8010 if STAGE == 'prod' else 8020