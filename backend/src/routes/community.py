"""
Valis AI - Community Routes
Collaboration and community features
"""

from flask import Blueprint, request, jsonify
import time
import uuid
from typing import Dict, List

# Initialize blueprint
community_bp = Blueprint('community', __name__)

# In-memory storage for demo (replace with database in production)
community_data = {
    'messages': [],
    'users': {},
    'templates': [],
    'projects': []
}

@community_bp.route('/chat/messages', methods=['GET'])
def get_community_messages():
    """
    Get recent community chat messages
    """
    try:
        # Get last 50 messages
        messages = community_data['messages'][-50:]
        return jsonify({'messages': messages})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/chat/send', methods=['POST'])
def send_community_message():
    """
    Send a message to community chat
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        username = data.get('username', 'Anonymous')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create message
        message_data = {
            'id': str(uuid.uuid4()),
            'username': username,
            'message': message,
            'timestamp': time.time(),
            'formatted_time': time.strftime('%H:%M', time.localtime())
        }
        
        community_data['messages'].append(message_data)
        
        # Keep only last 100 messages
        if len(community_data['messages']) > 100:
            community_data['messages'] = community_data['messages'][-100:]
        
        return jsonify({
            'success': True,
            'message': message_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/users/online', methods=['GET'])
def get_online_users():
    """
    Get list of online users
    """
    try:
        # Simulate online users
        online_users = [
            {'username': 'Alex_Dev', 'status': 'Building AI app'},
            {'username': 'Sarah_Designer', 'status': 'Creating website'},
            {'username': 'Mike_Founder', 'status': 'Planning startup'},
            {'username': 'Emma_Student', 'status': 'Learning React'}
        ]
        
        return jsonify({
            'online_count': len(online_users),
            'users': online_users
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/templates', methods=['GET'])
def get_community_templates():
    """
    Get community-shared templates
    """
    try:
        # Sample templates
        templates = [
            {
                'id': 'template_1',
                'name': 'SaaS Landing Page',
                'description': 'Modern SaaS landing page with pricing and features',
                'author': 'Alex_Dev',
                'category': 'Website',
                'tags': ['saas', 'landing', 'pricing'],
                'downloads': 245,
                'rating': 4.8,
                'created_at': time.time() - 86400
            },
            {
                'id': 'template_2',
                'name': 'E-commerce Store',
                'description': 'Complete e-commerce solution with cart and checkout',
                'author': 'Sarah_Designer',
                'category': 'Full-Stack',
                'tags': ['ecommerce', 'shopping', 'stripe'],
                'downloads': 189,
                'rating': 4.9,
                'created_at': time.time() - 172800
            },
            {
                'id': 'template_3',
                'name': 'Portfolio Website',
                'description': 'Clean portfolio website for developers and designers',
                'author': 'Mike_Founder',
                'category': 'Website',
                'tags': ['portfolio', 'personal', 'showcase'],
                'downloads': 156,
                'rating': 4.7,
                'created_at': time.time() - 259200
            }
        ]
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/templates/<template_id>', methods=['GET'])
def get_template_details(template_id):
    """
    Get detailed information about a template
    """
    try:
        # Sample template details
        template_details = {
            'id': template_id,
            'name': 'SaaS Landing Page',
            'description': 'Modern SaaS landing page with pricing and features',
            'author': 'Alex_Dev',
            'category': 'Website',
            'tags': ['saas', 'landing', 'pricing'],
            'downloads': 245,
            'rating': 4.8,
            'created_at': time.time() - 86400,
            'files': [
                'index.html',
                'styles.css',
                'script.js',
                'README.md'
            ],
            'preview_url': f'https://template-{template_id}.valis.ai',
            'code_url': f'https://github.com/valis-templates/{template_id}'
        }
        
        return jsonify(template_details)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/templates/<template_id>/use', methods=['POST'])
def use_template(template_id):
    """
    Use a community template in a new project
    """
    try:
        data = request.get_json()
        project_name = data.get('project_name', f'Project from {template_id}')
        
        # Simulate template usage
        project_id = str(uuid.uuid4())
        
        project_data = {
            'id': project_id,
            'name': project_name,
            'template_id': template_id,
            'created_at': time.time(),
            'status': 'created',
            'workspace_url': f'https://workspace-{project_id[:8]}.valis.ai'
        }
        
        community_data['projects'].append(project_data)
        
        return jsonify({
            'success': True,
            'project': project_data,
            'message': f'Template applied successfully! Your project "{project_name}" is ready.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/projects/share', methods=['POST'])
def share_project():
    """
    Share a project with the community
    """
    try:
        data = request.get_json()
        project_name = data.get('project_name', '')
        description = data.get('description', '')
        category = data.get('category', 'Other')
        tags = data.get('tags', [])
        author = data.get('author', 'Anonymous')
        
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        
        # Create shared project
        project_data = {
            'id': str(uuid.uuid4()),
            'name': project_name,
            'description': description,
            'author': author,
            'category': category,
            'tags': tags,
            'shared_at': time.time(),
            'views': 0,
            'likes': 0
        }
        
        community_data['templates'].append(project_data)
        
        return jsonify({
            'success': True,
            'project': project_data,
            'message': 'Project shared successfully with the community!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/projects/featured', methods=['GET'])
def get_featured_projects():
    """
    Get featured community projects
    """
    try:
        # Sample featured projects
        featured_projects = [
            {
                'id': 'project_1',
                'name': 'AI Chat Bot',
                'description': 'Intelligent chatbot with natural language processing',
                'author': 'Emma_Student',
                'category': 'AI/ML',
                'image': 'https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=400',
                'views': 1250,
                'likes': 89,
                'demo_url': 'https://ai-chatbot-demo.valis.ai'
            },
            {
                'id': 'project_2',
                'name': 'Task Management App',
                'description': 'Collaborative task management with real-time updates',
                'author': 'Alex_Dev',
                'category': 'Productivity',
                'image': 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400',
                'views': 980,
                'likes': 67,
                'demo_url': 'https://task-manager-demo.valis.ai'
            },
            {
                'id': 'project_3',
                'name': 'Weather Dashboard',
                'description': 'Beautiful weather dashboard with forecasts and maps',
                'author': 'Sarah_Designer',
                'category': 'Data Visualization',
                'image': 'https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=400',
                'views': 756,
                'likes': 45,
                'demo_url': 'https://weather-dashboard-demo.valis.ai'
            }
        ]
        
        return jsonify({'featured_projects': featured_projects})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/stats', methods=['GET'])
def get_community_stats():
    """
    Get community statistics
    """
    try:
        stats = {
            'total_users': 12847,
            'active_users': 1456,
            'projects_created': 8934,
            'templates_shared': 567,
            'messages_today': 234,
            'deployments_this_week': 1890
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get community leaderboard
    """
    try:
        leaderboard = [
            {
                'rank': 1,
                'username': 'Alex_Dev',
                'points': 2450,
                'projects': 23,
                'templates': 8,
                'badge': 'AI Pioneer'
            },
            {
                'rank': 2,
                'username': 'Sarah_Designer',
                'points': 2180,
                'projects': 19,
                'templates': 12,
                'badge': 'Design Master'
            },
            {
                'rank': 3,
                'username': 'Mike_Founder',
                'points': 1890,
                'projects': 15,
                'templates': 6,
                'badge': 'Startup Guru'
            },
            {
                'rank': 4,
                'username': 'Emma_Student',
                'points': 1650,
                'projects': 18,
                'templates': 4,
                'badge': 'Rising Star'
            }
        ]
        
        return jsonify({'leaderboard': leaderboard})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Get user notifications
    """
    try:
        notifications = [
            {
                'id': 'notif_1',
                'type': 'template_used',
                'message': 'Your template "SaaS Landing Page" was used 5 times today!',
                'timestamp': time.time() - 3600,
                'read': False
            },
            {
                'id': 'notif_2',
                'type': 'project_featured',
                'message': 'Your project "AI Chat Bot" is now featured!',
                'timestamp': time.time() - 7200,
                'read': False
            },
            {
                'id': 'notif_3',
                'type': 'community_milestone',
                'message': 'Valis AI community reached 10,000 users!',
                'timestamp': time.time() - 86400,
                'read': True
            }
        ]
        
        return jsonify({'notifications': notifications})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@community_bp.route('/health', methods=['GET'])
def community_health():
    """
    Community service health check
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Valis AI Community',
        'active_users': len(community_data['users']),
        'total_messages': len(community_data['messages']),
        'timestamp': time.time()
    })

