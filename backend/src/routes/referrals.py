"""
Valis AI - Referral Routes
API endpoints for referral program and credits
"""

from flask import Blueprint, request, jsonify
from core.referral_system import get_referral_system

referrals_bp = Blueprint('referrals', __name__)

@referrals_bp.route('/register', methods=['POST'])
def create_referral_profile():
    """Create referral profile for a new user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        email = data.get('email')
        name = data.get('name', '')
        
        if not user_id or not email:
            return jsonify({'error': 'User ID and email required'}), 400
        
        referral_system = get_referral_system()
        profile = referral_system.create_user_referral_profile(user_id, email, name)
        
        return jsonify({
            'success': True,
            'profile': {
                'user_id': profile['user_id'],
                'referral_code': profile['referral_code'],
                'referral_link': profile['referral_link'],
                'credits': profile['credits'],
                'tier': profile['tier'].value
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/signup', methods=['POST'])
def process_referral_signup():
    """Process a new user signup through referral"""
    try:
        data = request.get_json()
        new_user_id = data.get('new_user_id')
        new_user_email = data.get('new_user_email')
        referral_code = data.get('referral_code')
        new_user_name = data.get('new_user_name', '')
        
        if not new_user_id or not new_user_email or not referral_code:
            return jsonify({'error': 'New user ID, email, and referral code required'}), 400
        
        referral_system = get_referral_system()
        result = referral_system.process_referral_signup(
            new_user_id, 
            new_user_email, 
            referral_code, 
            new_user_name
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'referral_result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/share/<platform>', methods=['POST'])
def generate_social_share():
    """Generate social media share content"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        referral_system = get_referral_system()
        share_content = referral_system.generate_social_share_content(user_id, platform)
        
        if 'error' in share_content:
            return jsonify({'error': share_content['error']}), 400
        
        return jsonify({
            'success': True,
            'share_content': share_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/stats/<user_id>', methods=['GET'])
def get_referral_stats(user_id):
    """Get comprehensive referral statistics for a user"""
    try:
        referral_system = get_referral_system()
        stats = referral_system.get_user_referral_stats(user_id)
        
        if 'error' in stats:
            return jsonify({'error': stats['error']}), 404
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/leaderboard', methods=['GET'])
def get_referral_leaderboard():
    """Get referral leaderboard"""
    try:
        limit = int(request.args.get('limit', 10))
        
        referral_system = get_referral_system()
        leaderboard = referral_system.get_leaderboard(limit)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/credits/spend', methods=['POST'])
def spend_credits():
    """Spend user credits"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = data.get('amount')
        description = data.get('description', '')
        
        if not user_id or not amount:
            return jsonify({'error': 'User ID and amount required'}), 400
        
        referral_system = get_referral_system()
        result = referral_system.spend_credits(user_id, amount, description)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'transaction': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/credits/award', methods=['POST'])
def award_credits():
    """Award credits to a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = data.get('amount')
        reason = data.get('reason', '')
        
        if not user_id or not amount:
            return jsonify({'error': 'User ID and amount required'}), 400
        
        referral_system = get_referral_system()
        result = referral_system.award_credits(user_id, amount, reason)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'transaction': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@referrals_bp.route('/validate/<referral_code>', methods=['GET'])
def validate_referral_code(referral_code):
    """Validate a referral code"""
    try:
        referral_system = get_referral_system()
        
        # Check if referral code exists
        if referral_code in referral_system.referral_codes:
            referrer_id = referral_system.referral_codes[referral_code]
            referrer = referral_system.users.get(referrer_id)
            
            if referrer:
                return jsonify({
                    'success': True,
                    'valid': True,
                    'referrer': {
                        'user_id': referrer['user_id'],
                        'name': referrer['name'] or 'Anonymous',
                        'tier': referrer['tier'].value
                    }
                })
        
        return jsonify({
            'success': True,
            'valid': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

