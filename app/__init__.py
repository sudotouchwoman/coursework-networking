def run_app():
    
    from .blueprints import create_app
    from . import config
    settings = config.DevConfig
    app = create_app(settings=settings)

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG)

def load_json_config(path:str) -> dict:
    from json import loads
    with open(path, 'r') as confile:
        settings = loads(confile.read())
    return settings
