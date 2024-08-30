from pydantic_settings import BaseSettings
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path="../.env")

class LLMSettings(BaseSettings):
    api_key: str
    url: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create an instance of LLMSettings
settings = LLMSettings()

# Print the settings to verify they are loaded correctly
print(f"API Key: {settings.api_key}")
print(f"URL: {settings.url}")
