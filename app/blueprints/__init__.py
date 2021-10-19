def create_app():
    '''Create new app instance'''
    
    from .routes import app
    with app.app_context():
        from .home.routes import home_bp
        from .courses.routes import courses_bp
        from .hospital.routes import hospital_bp
        app.register_blueprint(home_bp, url_prefix='/home') 
        app.register_blueprint(courses_bp, url_prefix='/courses')
        app.register_blueprint(hospital_bp, url_prefix='/hospital')
        return app
