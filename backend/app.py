import os
from flask import Flask
from config import Config
from src.extensions import init_extensions
from src.utils.errors import register_error_handlers

def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from src.routes.auth import bp as auth_bp
    from src.routes.documents import bp as documents_bp
    from src.routes.analysis import bp as analysis_bp
    from src.routes.reports import bp as reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(reports_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'AI Research Critic API is running'}, 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return {'message': 'AI Research Critic API', 'version': '1.0.0'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
