def run_app():
    from view import create_app
    from . import config

    settings = config.DevConfig
    app = create_app(settings=settings)

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG)


def load_json_config(path: str) -> dict:
    from json import load
    with open(path, 'r') as confile:
        settings = load(confile)
    return settings
