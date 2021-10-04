from flask import Flask

def create_app():
    '''Create new app instance'''
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder='static/',
        template_folder='templates/')
    
    with app.app_context():
        from .home.routes import home_bp
        app.register_blueprint(home_bp, url_prefix='/home') 
        return app