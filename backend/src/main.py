import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp

# Import all Valis AI routes
from src.routes.autonomous import autonomous_bp
from src.routes.community import community_bp
from src.routes.files import files_bp
from src.routes.chat import chat_bp
from src.routes.referrals import referrals_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'valis-ai-unified-platform-secret-key'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(autonomous_bp, url_prefix='/api/autonomous')
app.register_blueprint(community_bp, url_prefix='/api/community')
app.register_blueprint(files_bp, url_prefix='/api/files')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(referrals_bp, url_prefix='/api/referrals')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# Valis AI Platform root endpoint
@app.route('/api')
def api_index():
    return jsonify({
        'service': 'Valis AI - Unified Platform',
        'version': '2.0.0',
        'description': 'The Ultimate Autonomous Intelligence Platform',
        'tagline': 'Where every thought becomes autonomous action',
        'endpoints': {
            'autonomous': '/api/autonomous',
            'community': '/api/community',
            'files': '/api/files',
            'chat': '/api/chat',
            'referrals': '/api/referrals',
            'users': '/api/users'
        },
        'features': [
            'Autonomous Intelligence with CodeAct Engine',
            'Multi-Mode Chat (Adaptive/Agent/Chat)',
            'AI-Powered File Processing',
            'Global Real-time Chat System',
            'Gamified Referral Program',
            'Community Collaboration',
            'Workspace Management',
            'Template Sharing'
        ],
        'competitive_advantages': [
            'Superior to Manus AI architecture',
            'Multi-model AI integration',
            'Real-time collaboration',
            'Advanced file analysis',
            'Comprehensive referral system',
            'Global community features'
        ]
    })

# Health check
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Valis AI Unified Platform',
        'components': {
            'autonomous_intelligence': 'active',
            'codeact_engine': 'active',
            'chat_modes': 'active',
            'file_processor': 'active',
            'global_chat': 'active',
            'referral_system': 'active',
            'community_features': 'active',
            'user_management': 'active'
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

