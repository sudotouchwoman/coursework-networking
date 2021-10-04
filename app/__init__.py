def run_app():
    
    from .blueprints import create_app, config
    app = create_app()
    settings = config.DevConfig()
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG)