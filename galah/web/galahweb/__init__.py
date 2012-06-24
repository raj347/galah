from flask import Flask
app = Flask("galah.web.galahweb")

if not app.config.from_envvar("GALAH_WEB_CONFIG", silent = True):
    try:
        app.config.from_pyfile("/etc/galah/web.config")
    except IOError:
        exit(
            "Environmental variable GALAH_WEB_CONFIG not set to valid file "
            "path and /etc/galah/web.config was not found. Either point "
            "GALAH_WEB_CONFIG at a valid config file or place your config "
            "file at /etc/galah/web.config."
        )

if "LOG_HANDLERS" in app.config:
    import logging
    
    # If a single handler was passed directly, convert it into a one-tuple
    if isinstance(app.config["LOG_HANDLERS"], logging.Handler):
        app.config["LOG_HANDLERS"] = (app.config["LOG_HANDLERS"], )
        
    # Add any handlers the user wants
    for i in app.config["LOG_HANDLERS"]:
        app.logger.addHandler(i)
            

# Plug the auth system into our app
from auth import login_manager
login_manager.setup_app(app)

import views