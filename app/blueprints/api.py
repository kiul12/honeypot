from datetime import datetime
import hmac
import hashlib
import time

from flask import Blueprint, request, jsonify, current_app
from ..extensions import db, limiter
from ..models import AttackEvent, AttackerProfile


api_bp = Blueprint('api', __name__)


def verify_api_signature():
    """验证API签名"""
    signature = request.headers.get('X-API-Signature')
    timestamp = request.headers.get('X-API-Timestamp')
    
    if not signature or not timestamp:
        return False
    
    # 检查时间戳（5分钟内有效）
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > 300:  # 5分钟
            return False
    except ValueError:
        return False
    
    # 验证签名
    secret = current_app.config.get('API_SECRET_KEY', 'default-secret')
    expected_signature = hmac.new(
        secret.encode(),
        f"{timestamp}{request.get_data()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def get_or_create_attacker(ip_address: str, user_agent: str | None):
    profile = AttackerProfile.query.filter_by(ip_address=ip_address).first()
    if profile:
        profile.last_seen = datetime.utcnow()
        if user_agent:
            profile.user_agent = user_agent
        return profile
    profile = AttackerProfile(
        ip_address=ip_address,
        user_agent=user_agent or '',
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )
    db.session.add(profile)
    return profile


@api_bp.route('/capture', methods=['POST'])
@limiter.limit("100 per minute")
def capture():
    # 验证API签名
    if not verify_api_signature():
        return jsonify({'error': 'Invalid signature'}), 401
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    json_payload = request.get_json(silent=True) or {}

    profile = get_or_create_attacker(ip_address, user_agent)

    event = AttackEvent(
        ip_address=ip_address,
        method=request.method,
        path=request.path,
        headers=dict(request.headers),
        payload=json_payload,
        honeypot_service=json_payload.get('service') or 'web',
        signature=json_payload.get('signature'),
        severity=json_payload.get('severity') or 'low',
        attacker=profile,
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'status': 'ok', 'event_id': event.id})


