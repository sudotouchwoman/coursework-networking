def create_app(settings):
    '''Create new app instance'''
    if settings is None: raise ValueError

    from .routes import app
    with app.app_context():

        app.config['SECRET_KEY'] = settings.SECRET_KEY
        app.config['POLICIES'] = settings.POLICIES
        app.config['DB'] = settings.DB
        app.config['QUERIES'] = settings.QUERIES

        from .home.routes import home_bp
        from .courses.routes import courses_bp
        from .hospital.routes import hospital_bp
        from .auth.routes import auth_bp
        
        app.register_blueprint(home_bp, url_prefix='/home') 
        app.register_blueprint(courses_bp, url_prefix='/courses')
        app.register_blueprint(hospital_bp, url_prefix='/hospital')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        return app
