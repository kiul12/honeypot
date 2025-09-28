"""
后台任务模块
"""
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import AttackEvent, AttackerProfile


def cleanup_old_data(days=30):
    """清理指定天数前的数据"""
    app = create_app()
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 删除旧的攻击事件
        old_events = AttackEvent.query.filter(AttackEvent.timestamp < cutoff_date).all()
        for event in old_events:
            db.session.delete(event)
        
        # 删除没有攻击事件的攻击者档案
        old_profiles = AttackerProfile.query.filter(
            AttackerProfile.last_seen < cutoff_date,
            ~AttackerProfile.attacks.any()
        ).all()
        for profile in old_profiles:
            db.session.delete(profile)
        
        db.session.commit()
        print(f"清理了 {len(old_events)} 个攻击事件和 {len(old_profiles)} 个攻击者档案")


def generate_daily_report():
    """生成每日报告"""
    app = create_app()
    with app.app_context():
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # 统计昨天的数据
        events_count = AttackEvent.query.filter(
            db.func.date(AttackEvent.timestamp) == yesterday
        ).count()
        
        new_attackers = AttackerProfile.query.filter(
            db.func.date(AttackerProfile.first_seen) == yesterday
        ).count()
        
        # 这里可以添加邮件发送或其他通知逻辑
        print(f"每日报告 - {yesterday}:")
        print(f"  攻击事件: {events_count}")
        print(f"  新攻击者: {new_attackers}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'cleanup':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            cleanup_old_data(days)
        elif sys.argv[1] == 'report':
            generate_daily_report()
    else:
        print("用法: python tasks.py [cleanup|report] [days]")
