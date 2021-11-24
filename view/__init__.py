def create_app(settings):
    '''Create new app instance'''
    if settings is None: raise ValueError('Application factory abort: bad config provided')

    from .routes import app
    with app.app_context():

        app.config['SECRET_KEY'] = settings.SECRET_KEY
        app.config['POLICIES'] = settings.POLICIES
        app.config['DB'] = settings.DB
        app.config['QUERIES'] = settings.QUERIES

        from .hospital.routes import hospital_bp
        from .patiens.routes import patients_bp
        from .auth.routes import auth_bp
        
        app.register_blueprint(hospital_bp, url_prefix='/hospital')
        app.register_blueprint(patients_bp, url_prefix='/patient')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        return app
