
from decouple import config

env = config("ENVIRONMENT", default="development")

if env == "production":
    from .prod import *
elif env == "development":
    from .dev import *
