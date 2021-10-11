def create_app():
    '''Create new app instance'''
    
    from .routes import app
    with app.app_context():
        from .home.routes import home_bp
        from .user.routes import user_bp
        app.register_blueprint(home_bp, url_prefix='/home') 
        app.register_blueprint(user_bp, url_prefix='/user') 
        return app
