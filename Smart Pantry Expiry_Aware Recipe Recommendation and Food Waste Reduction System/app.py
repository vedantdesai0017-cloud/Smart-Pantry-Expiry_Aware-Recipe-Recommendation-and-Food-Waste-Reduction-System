from flask import Flask, session, redirect, url_for, render_template
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.pantry import pantry_bp
from routes.recipes import recipes_bp
from routes.waste import waste_bp
from routes.analytics import analytics_bp
from routes.expiring import expiring_bp
from routes.ai_assistant import ai_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pantry_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(waste_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(expiring_bp)
    app.register_blueprint(ai_bp)
    
    with app.app_context():
        db.create_all()
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
