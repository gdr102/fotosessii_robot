import os

from dotenv import load_dotenv

load_dotenv()

TOKEN_POLZA = os.getenv('TOKEN_POLZA')
TOKEN_TG = os.getenv('TOKEN_TG')
ENGINE = os.getenv('ENGINE')
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY', 'XTR')
ECHO = os.getenv('ECHO', 'False').lower() in ('1', 'true', 'yes')
ADMIN_REFUND_CHAT_ID = int(os.getenv('ADMIN_REFUND_CHAT_ID'))
ADMIN_PUBLIC_CHANNEL_ID = int(os.getenv('ADMIN_PUBLIC_CHANNEL_ID'))
PAYMENT_MIN_STARS = int(os.getenv('PAYMENT_MIN_STARS', 50))
ADMINS = [int(x.strip()) for x in os.getenv('ADMINS', '').split(',') if x.strip()]
BOT_URL = os.getenv('BOT_URL', 'FotosessII_robot')
CHANNEL_URL = os.getenv('CHANNEL_URL', 'FotosessII_Pro')

if not TOKEN_TG:
    raise RuntimeError('Environment variable TOKEN_TG is required')
if not ENGINE:
    raise RuntimeError('Environment variable ENGINE is required')