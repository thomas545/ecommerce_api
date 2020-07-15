from .staging import *


DEBUG = False


"""
Finally, create a googlebot user. 
This account will be used when Googlebot is automatically logged in. 
If you don't create an account, then one will be created automatically.

NB If you wish to disable the Google Cache feature, create a robots.txt with Noarchive . Eg:

User-agent: *
Disallow:
Noarchive: /restricted-content/
"""
MIDDLEWARE += [
    "core.middlewares.GooglebotMiddleware",
]

