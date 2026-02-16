"""Run this script on the server to create the .env file."""
import os

DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(DIR, ".env")

# Anthropic key (split to avoid terminal truncation)
ak = "sk-ant-api03-0OUbvEcfSqTK1Df"
ak += "-oq74TmR-36V6GkJYIzgeY0kjaAE"
ak += "F5Z5_nBl8OfIhGYYPRyEqUJ32a_n"
ak += "OrFbZttr2PFj90A-KxHhyQAA"

# WhatsApp token
wa = "EAAmsKUuLopgBQvltjueIsnMtoqs"
wa += "5MhnlxmZCn1CZC2eIhgZB8a6SJ9"
wa += "AUTiDXBIJmTL6bZBJRkz1vSqhtXW"
wa += "RUFCHhZByeHUCQSh0iSbKamHLNSR"
wa += "8s93wOX9uofyFXSAGrh4awtHt2fv"
wa += "2lxe1MzjlZA6kVMyi0avZCT0m8DZB"
wa += "FV3JIoXkzR56rXKAv7Vhks3o9OFf"
wa += "QpJy7mZBmrGg7ZB690AQiZAPE4sOU"
wa += "pxum0T8FRAqZCrbtpfWEvdZArGYyz"
wa += "YyOd1PB7HWd1E7xwskpj3rOudQ3E"
wa += "iohPx2ZBl"

content = f"""ANTHROPIC_API_KEY={ak}
WHATSAPP_TOKEN={wa}
WHATSAPP_PHONE_NUMBER_ID=1056771637509201
WHATSAPP_VERIFY_TOKEN=fiberperu_webhook_2024
WISPHUB_API_URL=https://api.wisphub.app/api
WISPHUB_API_TOKEN=Aef4xvDp.KBX6PKTl3qRMRLVj41dZGeys1ZGGOyTz
WISPHUB_COMPANY_ID=26779
"""

with open(ENV_PATH, "w") as f:
    f.write(content)

print(f"OK - .env created at {ENV_PATH}")
print(f"WhatsApp token length: {len(wa)}")
print(f"Anthropic key length: {len(ak)}")
