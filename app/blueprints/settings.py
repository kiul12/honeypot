from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..extensions import db
from ..models import User
from ..forms import ChangePasswordForm
import hashlib

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('密码修改成功', 'success')
        else:
            flash('原密码错误', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/update-notifications', methods=['POST'])
@login_required
def update_notifications():
    email_notifications = request.form.get('email_notifications') == 'on'
    # Store in user profile or separate settings table
    current_user.email_notifications = email_notifications
    db.session.commit()
    flash('通知设置已更新', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Delete user account
    db.session.delete(current_user)
    db.session.commit()
    flash('账号已删除', 'success')
    return redirect(url_for('auth.login'))


@settings_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    theme = request.json.get('theme', 'light')
    # Store theme preference in user profile or session
    current_user.theme_preference = theme
    db.session.commit()
    return jsonify({'status': 'success', 'theme': theme})
