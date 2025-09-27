# Australian Biodiversity Analytics Platform Configuration

# API Settings
INATURALIST_BASE_URL = "https://api.inaturalist.org/v1/observations"
AUSTRALIA_PLACE_ID = "6744"
API_REQUEST_DELAY = 1  # seconds between API calls

# Database Settings
DATABASE_PATH = "data/aussie_wildlife.db"

# Collection Settings
DEFAULT_KOALA_LIMIT = 25
DEFAULT_KANGAROO_LIMIT = 20
DEFAULT_QUERY_LIMIT = 50

# Species Configuration
AUSTRALIAN_SPECIES = {
    "koala": {
        "scientific_name": "Phascolarctos cinereus",
        "common_name": "Koala",
        "default_limit": 25
    },
    "kangaroo": {
        "scientific_name": "Macropus",
        "common_name": "Kangaroo/Wallaby",
        "default_limit": 20
    }
}

# Analysis Settings
DEFAULT_RECENT_DAYS = 7
DEFAULT_LOCATION_LIMIT = 10
