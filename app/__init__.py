def run_app():
    
    from .apps import create_app, config
    app = create_app()
    settings = config.DevConfig()
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG)