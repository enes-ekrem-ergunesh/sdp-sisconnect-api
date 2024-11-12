"""
config.json file structure:
{
    "HOST": "<host>",
    "PORT": <port>,
    "USER": "<user>",
    "PASSWORD": "<password>",
    "DATABASE": "<database>",
    "SECRET": "<secret>"
}
"""

import os
import json

# Path to your config.json file
CONFIG_FILE_PATH = 'config.json'


def load_config():
    # Load environment variables
    env_config = {
        "HOST": os.getenv("HOST"),
        "PORT": os.getenv("PORT"),
        "USER": os.getenv("USER"),
        "PASSWORD": os.getenv("PASSWORD"),
        "DATABASE": os.getenv("DATABASE"),
        "SECRET": os.getenv("SECRET"),
    }

    # Check if all environment variables are set
    if all(env_config.values()):
        return env_config
    else:
        # Load from config.json if any environment variable is missing
        with open(CONFIG_FILE_PATH, 'r') as file:
            json_config = json.load(file)
            return json_config


# Load configuration
config = load_config()