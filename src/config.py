from dotenv import load_dotenv, dotenv_values, find_dotenv
load_dotenv(find_dotenv(), override=True)
import os


STAGE: str = os.getenv('STAGE', 'dev')

QDRANT_URL: str = os.getenv('QDRANT_URL', 'http://localhost:6333')

QDRANT_NAMESPACE = 'gossip_prod' if STAGE == 'prod' else 'gossip_dev'

PORT= 8010 if STAGE == 'prod' else 8020