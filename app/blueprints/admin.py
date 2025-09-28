from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required  # pyright: ignore[reportMissingImports]

from ..extensions import db
from ..models import AttackEvent, AttackerProfile
from datetime import datetime
import random


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_attacks = AttackEvent.query.count()
    unique_attackers = AttackerProfile.query.count()
    recent_attacks = AttackEvent.query.order_by(AttackEvent.timestamp.desc()).limit(20).all()
    
    # 获取攻击类型统计
    attack_types = db.session.query(
        AttackEvent.honeypot_service,
        db.func.count(AttackEvent.id).label('count')
    ).group_by(AttackEvent.honeypot_service).all()
    
    # 获取地区统计
    country_stats = db.session.query(
        AttackerProfile.country,
        db.func.count(AttackEvent.id).label('count')
    ).join(AttackEvent, AttackerProfile.id == AttackEvent.attacker_id).group_by(AttackerProfile.country).all()
    
    # 获取严重级别统计
    severity_stats = db.session.query(
        AttackEvent.severity,
        db.func.count(AttackEvent.id).label('count')
    ).group_by(AttackEvent.severity).all()
    
    # 获取最新更新时间
    latest_update = AttackEvent.query.order_by(AttackEvent.timestamp.desc()).first()
    
    return render_template('dashboard.html', 
                         total_attacks=total_attacks, 
                         unique_attackers=unique_attackers, 
                         recent_attacks=recent_attacks,
                         attack_types=attack_types,
                         country_stats=country_stats,
                         severity_stats=severity_stats,
                         latest_update=latest_update)


@admin_bp.route('/attackers')
@login_required
def attackers():
    profiles = AttackerProfile.query.order_by(AttackerProfile.last_seen.desc()).all()
    return render_template('attackers.html', profiles=profiles)


@admin_bp.route('/attacks')
@login_required
def attacks():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    ip = request.args.get('ip')
    method = request.args.get('method')

    query = AttackEvent.query
    if ip:
        query = query.filter(AttackEvent.ip_address.contains(ip))
    if method:
        query = query.filter(AttackEvent.method == method)

    pagination = query.order_by(AttackEvent.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('attacks.html', events=pagination.items, pagination=pagination, ip=ip or '', method=method or '')


@admin_bp.route('/stats')
@login_required
def stats():
    # 数据统计模块
    total_events = AttackEvent.query.count()
    total_attackers = AttackerProfile.query.count()
    latest_event = AttackEvent.query.order_by(AttackEvent.timestamp.desc()).first()
    return render_template('stats.html', total_events=total_events, total_attackers=total_attackers, latest_event=latest_event)


@admin_bp.route('/database')
@login_required
def database():
    # 数据库页面：展示各表与行数
    tables = []
    try:
        # 获取表名
        result = db.session.execute(db.text('SHOW TABLES'))
        table_names = [row[0] for row in result]
        for name in table_names:
            try:
                count = db.session.execute(db.text(f'SELECT COUNT(*) FROM `{name}`')).scalar() or 0
            except Exception:
                count = 'N/A'
            tables.append({'name': name, 'rows': count})
    except Exception as e:
        tables = []
        flash(f'读取数据库结构失败: {e}', 'error')
    return render_template('database.html', tables=tables)


@admin_bp.route('/map')
@login_required
def map():
    # 获取攻击数据用于地图显示
    rows = (
        db.session.query(
            AttackerProfile.country,
            db.func.count(AttackEvent.id).label('count')
        )
        .join(AttackEvent, AttackerProfile.id == AttackEvent.attacker_id)
        .group_by(AttackerProfile.country)
        .all()
    )
    attacks_by_country = [{'country': r[0] or 'Unknown', 'count': int(r[1] or 0)} for r in rows]

    return render_template('map.html', attacks_by_country=attacks_by_country)


@admin_bp.route('/simulate-attack', methods=['POST'])
@login_required
def simulate_attack():
    # 生成模拟攻击数据
    ip = request.form.get('ip') or f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"
    ua = request.form.get('ua') or 'Mozilla/5.0 (Simulation)'
    country = request.form.get('country') or random.choice(['CN','US','RU','IN','DE','FR','GB','BR','JP','KR'])
    severity = request.form.get('severity') or random.choice(['low','medium','high'])

    profile = AttackerProfile.query.filter_by(ip_address=ip).first()
    if not profile:
        profile = AttackerProfile(ip_address=ip, user_agent=ua, country=country, city='', first_seen=datetime.utcnow(), last_seen=datetime.utcnow())
        db.session.add(profile)
    else:
        profile.last_seen = datetime.utcnow()
        profile.country = country or profile.country

    event = AttackEvent(
        ip_address=ip,
        method='GET',
        path='/honeypot',
        headers={'User-Agent': ua},
        payload={'simulated': True},
        honeypot_service='web',
        signature='sim-test',
        severity=severity,
        attacker=profile,
    )
    db.session.add(event)
    db.session.commit()
    flash('已生成一条模拟攻击数据', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/export-stats')
@login_required
def export_stats():
    # 导出简要统计为txt
    total_events = AttackEvent.query.count()
    total_attackers = AttackerProfile.query.count()
    by_country = (
        db.session.query(AttackerProfile.country, db.func.count(AttackEvent.id))
        .join(AttackEvent, AttackerProfile.id == AttackEvent.attacker_id)
        .group_by(AttackerProfile.country)
        .all()
    )
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    lines = [
        f"Export Time: {now}",
        f"Total Events: {total_events}",
        f"Total Attackers: {total_attackers}",
        "By Country:",
    ]
    for c, cnt in by_country:
        lines.append(f"  {c or 'Unknown'}: {cnt}")
    content = "\n".join(lines)
    resp = make_response(content)
    filename = datetime.utcnow().strftime('stats-%Y%m%d-%H%M%S.txt')
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return resp

# 设置settings页面
@admin_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')