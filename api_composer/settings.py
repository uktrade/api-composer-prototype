from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret, URL

config = Config(".env")

DEBUG = config('DEBUG', cast=bool, default=False)

DATA_HUB_API_URL = config('DATA_HUB_API_URL', cast=URL)
DATA_HUB_API_HAWK_ID = config('DATA_HUB_API_HAWK_ID')
DATA_HUB_API_HAWK_KEY = config('DATA_HUB_API_HAWK_KEY', cast=Secret)

DATA_SCIENCE_API_URL = config('DATA_SCIENCE_API_URL', cast=URL)
DATA_SCIENCE_API_HAWK_ID = config('DATA_SCIENCE_API_HAWK_ID')
DATA_SCIENCE_API_HAWK_KEY = config('DATA_SCIENCE_API_HAWK_KEY', cast=Secret)
