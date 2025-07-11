"""
Valis AI - Referral System
Advanced referral program with credits, social sharing, and gamification
"""

import uuid
import time
import json
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ReferralTier(Enum):
    BRONZE = "bronze"    # 1-9 referrals
    SILVER = "silver"    # 10-24 referrals  
    GOLD = "gold"        # 25-49 referrals
    PLATINUM = "platinum" # 50-99 referrals
    DIAMOND = "diamond"   # 100+ referrals

@dataclass
class ReferralReward:
    credits: int
    bonus_multiplier: float
    special_features: List[str]
    tier_name: str

class ReferralSystem:
    """
    Advanced referral system with tiered rewards and social features
    """
    
    def __init__(self):
        self.users = {}
        self.referral_codes = {}
        self.referral_history = {}
        self.social_shares = {}
        
        # Reward tiers
        self.tier_rewards = {
            ReferralTier.BRONZE: ReferralReward(
                credits=500,
                bonus_multiplier=1.0,
                special_features=["Basic referral tracking"],
                tier_name="Bronze Advocate"
            ),
            ReferralTier.SILVER: ReferralReward(
                credits=750,
                bonus_multiplier=1.25,
                special_features=["Priority support", "Beta features"],
                tier_name="Silver Ambassador"
            ),
            ReferralTier.GOLD: ReferralReward(
                credits=1000,
                bonus_multiplier=1.5,
                special_features=["Custom branding", "Advanced analytics"],
                tier_name="Gold Champion"
            ),
            ReferralTier.PLATINUM: ReferralReward(
                credits=1500,
                bonus_multiplier=2.0,
                special_features=["White-label access", "API priority"],
                tier_name="Platinum Elite"
            ),
            ReferralTier.DIAMOND: ReferralReward(
                credits=2500,
                bonus_multiplier=3.0,
                special_features=["Revenue sharing", "Co-marketing opportunities"],
                tier_name="Diamond Legend"
            )
        }
    
    def create_user_referral_profile(self, user_id: str, email: str, name: str = "") -> Dict[str, Any]:
        """Create referral profile for a new user"""
        
        # Generate unique referral code
        referral_code = self._generate_referral_code(user_id, email)
        
        user_profile = {
            'user_id': user_id,
            'email': email,
            'name': name,
            'referral_code': referral_code,
            'credits': 1500,  # Starting credits
            'total_referrals': 0,
            'successful_referrals': 0,
            'tier': ReferralTier.BRONZE,
            'tier_progress': 0,
            'lifetime_credits_earned': 0,
            'created_at': time.time(),
            'last_activity': time.time(),
            'referred_by': None,
            'referral_link': f"https://valis.ai/join?ref={referral_code}",
            'social_shares': {
                'twitter': 0,
                'linkedin': 0,
                'facebook': 0,
                'email': 0,
                'direct_link': 0
            },
            'achievements': [],
            'bonus_multiplier': 1.0
        }
        
        self.users[user_id] = user_profile
        self.referral_codes[referral_code] = user_id
        
        return user_profile
    
    def process_referral_signup(self, new_user_id: str, new_user_email: str, referral_code: str, new_user_name: str = "") -> Dict[str, Any]:
        """Process a new user signup through referral"""
        
        # Validate referral code
        if referral_code not in self.referral_codes:
            return {'error': 'Invalid referral code'}
        
        referrer_id = self.referral_codes[referral_code]
        
        if referrer_id not in self.users:
            return {'error': 'Referrer not found'}
        
        # Create profile for new user
        new_user_profile = self.create_user_referral_profile(new_user_id, new_user_email, new_user_name)
        new_user_profile['referred_by'] = referrer_id
        new_user_profile['credits'] += 500  # Bonus for being referred
        
        # Update referrer
        referrer = self.users[referrer_id]
        referrer['total_referrals'] += 1
        referrer['successful_referrals'] += 1
        referrer['last_activity'] = time.time()
        
        # Calculate rewards
        base_reward = 500
        tier_multiplier = self.tier_rewards[referrer['tier']].bonus_multiplier
        total_reward = int(base_reward * tier_multiplier)
        
        referrer['credits'] += total_reward
        referrer['lifetime_credits_earned'] += total_reward
        
        # Update tier
        self._update_user_tier(referrer_id)
        
        # Record referral
        referral_record = {
            'referral_id': str(uuid.uuid4()),
            'referrer_id': referrer_id,
            'referred_user_id': new_user_id,
            'referral_code': referral_code,
            'credits_awarded': total_reward,
            'tier_at_time': referrer['tier'].value,
            'timestamp': time.time(),
            'status': 'completed'
        }
        
        if referrer_id not in self.referral_history:
            self.referral_history[referrer_id] = []
        
        self.referral_history[referrer_id].append(referral_record)
        
        # Check for achievements
        self._check_achievements(referrer_id)
        
        return {
            'referrer': {
                'user_id': referrer_id,
                'credits_earned': total_reward,
                'new_tier': referrer['tier'].value,
                'total_referrals': referrer['total_referrals']
            },
            'new_user': {
                'user_id': new_user_id,
                'starting_credits': new_user_profile['credits'],
                'referred_by': referrer_id
            },
            'referral_record': referral_record
        }
    
    def generate_social_share_content(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Generate social media share content"""
        
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        referral_link = user['referral_link']
        
        share_content = {
            'twitter': {
                'text': f"🚀 Just discovered Valis AI - the future of autonomous intelligence! Get 500 free credits when you join: {referral_link} #ValisAI #AI #Automation",
                'hashtags': ["ValisAI", "AI", "Automation", "FutureOfWork"],
                'url': referral_link
            },
            'linkedin': {
                'title': "Discover Valis AI - Autonomous Intelligence Platform",
                'description': f"I'm using Valis AI for autonomous task execution and it's incredible! Join me and get 500 free credits to start building with AI: {referral_link}",
                'url': referral_link
            },
            'facebook': {
                'quote': f"🤖 The future is here with Valis AI! Autonomous intelligence that actually works. Get 500 free credits: {referral_link}",
                'url': referral_link
            },
            'email': {
                'subject': "You need to see this AI platform - Valis AI",
                'body': f"""Hey!

I've been using this incredible AI platform called Valis AI and thought you'd love it. It's like having an autonomous AI assistant that can actually build things for you.

Here's what makes it special:
• Autonomous task execution
• Real-time collaboration
• Advanced AI capabilities
• Global community

You can get 500 free credits to try it out using my referral link: {referral_link}

Let me know what you think!

Best,
{user['name'] or 'A friend'}""",
                'url': referral_link
            },
            'whatsapp': {
                'text': f"🚀 Check out Valis AI - autonomous intelligence platform that's changing everything! Get 500 free credits: {referral_link}",
                'url': referral_link
            }
        }
        
        # Track share
        if platform in user['social_shares']:
            user['social_shares'][platform] += 1
        
        # Record social share
        share_record = {
            'share_id': str(uuid.uuid4()),
            'user_id': user_id,
            'platform': platform,
            'timestamp': time.time(),
            'referral_code': user['referral_code']
        }
        
        if user_id not in self.social_shares:
            self.social_shares[user_id] = []
        
        self.social_shares[user_id].append(share_record)
        
        return {
            'platform': platform,
            'content': share_content.get(platform, {}),
            'share_record': share_record,
            'total_shares': sum(user['social_shares'].values())
        }
    
    def _generate_referral_code(self, user_id: str, email: str) -> str:
        """Generate unique referral code"""
        # Create a hash from user info and timestamp
        data = f"{user_id}_{email}_{time.time()}"
        hash_object = hashlib.md5(data.encode())
        hash_hex = hash_object.hexdigest()
        
        # Take first 8 characters and make it readable
        code = hash_hex[:8].upper()
        
        # Ensure uniqueness
        while code in self.referral_codes:
            data = f"{data}_retry"
            hash_object = hashlib.md5(data.encode())
            code = hash_object.hexdigest()[:8].upper()
        
        return code
    
    def _update_user_tier(self, user_id: str):
        """Update user tier based on referral count"""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        referral_count = user['successful_referrals']
        
        # Determine new tier
        if referral_count >= 100:
            new_tier = ReferralTier.DIAMOND
        elif referral_count >= 50:
            new_tier = ReferralTier.PLATINUM
        elif referral_count >= 25:
            new_tier = ReferralTier.GOLD
        elif referral_count >= 10:
            new_tier = ReferralTier.SILVER
        else:
            new_tier = ReferralTier.BRONZE
        
        # Update if tier changed
        if new_tier != user['tier']:
            old_tier = user['tier']
            user['tier'] = new_tier
            user['bonus_multiplier'] = self.tier_rewards[new_tier].bonus_multiplier
            
            # Award tier upgrade bonus
            tier_bonus = self.tier_rewards[new_tier].credits
            user['credits'] += tier_bonus
            user['lifetime_credits_earned'] += tier_bonus
            
            # Add achievement
            achievement = {
                'achievement_id': str(uuid.uuid4()),
                'type': 'tier_upgrade',
                'title': f"Promoted to {self.tier_rewards[new_tier].tier_name}!",
                'description': f"Upgraded from {old_tier.value} to {new_tier.value}",
                'credits_awarded': tier_bonus,
                'timestamp': time.time()
            }
            
            user['achievements'].append(achievement)
        
        # Update progress to next tier
        if new_tier == ReferralTier.BRONZE:
            user['tier_progress'] = min(referral_count / 10, 1.0)
        elif new_tier == ReferralTier.SILVER:
            user['tier_progress'] = min((referral_count - 10) / 15, 1.0)
        elif new_tier == ReferralTier.GOLD:
            user['tier_progress'] = min((referral_count - 25) / 25, 1.0)
        elif new_tier == ReferralTier.PLATINUM:
            user['tier_progress'] = min((referral_count - 50) / 50, 1.0)
        else:  # DIAMOND
            user['tier_progress'] = 1.0
    
    def _check_achievements(self, user_id: str):
        """Check and award achievements"""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        referral_count = user['successful_referrals']
        
        # Milestone achievements
        milestones = [1, 5, 10, 25, 50, 100, 250, 500, 1000]
        
        for milestone in milestones:
            if referral_count >= milestone:
                # Check if achievement already exists
                existing = any(
                    a['type'] == 'milestone' and a.get('milestone') == milestone 
                    for a in user['achievements']
                )
                
                if not existing:
                    achievement = {
                        'achievement_id': str(uuid.uuid4()),
                        'type': 'milestone',
                        'milestone': milestone,
                        'title': f"{milestone} Referrals Champion!",
                        'description': f"Successfully referred {milestone} users to Valis AI",
                        'credits_awarded': milestone * 100,
                        'timestamp': time.time()
                    }
                    
                    user['achievements'].append(achievement)
                    user['credits'] += achievement['credits_awarded']
                    user['lifetime_credits_earned'] += achievement['credits_awarded']
    
    def get_user_referral_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive referral statistics for a user"""
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        tier_info = self.tier_rewards[user['tier']]
        
        # Calculate next tier requirements
        next_tier_info = None
        if user['tier'] != ReferralTier.DIAMOND:
            tier_order = [ReferralTier.BRONZE, ReferralTier.SILVER, ReferralTier.GOLD, ReferralTier.PLATINUM, ReferralTier.DIAMOND]
            current_index = tier_order.index(user['tier'])
            if current_index < len(tier_order) - 1:
                next_tier = tier_order[current_index + 1]
                next_tier_info = {
                    'tier': next_tier.value,
                    'name': self.tier_rewards[next_tier].tier_name,
                    'required_referrals': [10, 25, 50, 100][current_index] if current_index < 4 else None
                }
        
        return {
            'user_id': user_id,
            'referral_code': user['referral_code'],
            'referral_link': user['referral_link'],
            'current_tier': {
                'tier': user['tier'].value,
                'name': tier_info.tier_name,
                'credits_per_referral': tier_info.credits,
                'bonus_multiplier': tier_info.bonus_multiplier,
                'special_features': tier_info.special_features
            },
            'next_tier': next_tier_info,
            'stats': {
                'total_referrals': user['total_referrals'],
                'successful_referrals': user['successful_referrals'],
                'current_credits': user['credits'],
                'lifetime_credits_earned': user['lifetime_credits_earned'],
                'tier_progress': user['tier_progress']
            },
            'social_shares': user['social_shares'],
            'achievements': user['achievements'],
            'referral_history': self.referral_history.get(user_id, [])
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get referral leaderboard"""
        # Sort users by successful referrals
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: x['successful_referrals'],
            reverse=True
        )
        
        leaderboard = []
        for i, user in enumerate(sorted_users[:limit]):
            leaderboard.append({
                'rank': i + 1,
                'user_id': user['user_id'],
                'name': user['name'] or 'Anonymous',
                'referrals': user['successful_referrals'],
                'tier': user['tier'].value,
                'tier_name': self.tier_rewards[user['tier']].tier_name,
                'lifetime_credits': user['lifetime_credits_earned']
            })
        
        return leaderboard
    
    def spend_credits(self, user_id: str, amount: int, description: str = "") -> Dict[str, Any]:
        """Spend user credits"""
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        
        if user['credits'] < amount:
            return {'error': 'Insufficient credits'}
        
        user['credits'] -= amount
        user['last_activity'] = time.time()
        
        return {
            'user_id': user_id,
            'credits_spent': amount,
            'remaining_credits': user['credits'],
            'description': description,
            'timestamp': time.time()
        }
    
    def award_credits(self, user_id: str, amount: int, reason: str = "") -> Dict[str, Any]:
        """Award credits to a user"""
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        user = self.users[user_id]
        user['credits'] += amount
        user['lifetime_credits_earned'] += amount
        user['last_activity'] = time.time()
        
        return {
            'user_id': user_id,
            'credits_awarded': amount,
            'total_credits': user['credits'],
            'reason': reason,
            'timestamp': time.time()
        }

# Global referral system instance
referral_system = None

def get_referral_system() -> ReferralSystem:
    """Get or create the global referral system instance"""
    global referral_system
    if referral_system is None:
        referral_system = ReferralSystem()
    return referral_system

