import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from gym_manager.database import get_db_session, Member, Payment, Admin
from gym_manager.members import add_member, get_all_members, get_member_by_id, delete_member
from gym_manager.payments import record_payment, get_all_payments, delete_payment
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')

# --- SECURITY IMPROVEMENT ---
# Load the secret key from an environment variable for security.
# If it's not set, use a default value ONLY for local development.
# For deployment, you MUST set a proper SECRET_KEY environment variable.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a-default-fallback-key-for-dev')

# --- LOGIN MANAGER SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to /login if user is not authenticated

@login_manager.user_loader
def load_user(user_id):
    session = get_db_session()
    # Use session.get() for primary key lookups, it's slightly more efficient
    user = session.get(Admin, int(user_id))
    session.close()
    return user

# --- AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session = get_db_session()
        user = session.query(Admin).filter_by(username=username).first()
        session.close()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # Redirect to the page the user was trying to access, or to the index
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login failed. Check username and password.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- HELPER FUNCTION ---
def calculate_membership_fee(membership_type):
    """Calculate membership fee based on type and duration"""
    rates = {"Monthly": 30, "Quarterly": 80, "Annual": 300}
    return rates.get(membership_type, 0)

# --- API ROUTES (Not protected by login for potential external use) ---
@app.route('/api/members', methods=['GET'])
def api_get_members():
    try:
        members = get_all_members()
        return jsonify([{
            'id': m.id,
            'name': f"{m.first_name} {m.last_name}",
            'email': m.email,
            'membership_type': m.membership_type
        } for m in members])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['GET'])
def api_get_member(member_id):
    try:
        member = get_member_by_id(member_id)
        if member:
            return jsonify({
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'email': member.email,
                'membership_type': member.membership_type
            })
        return jsonify({'error': 'Member not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- PROTECTED APPLICATION ROUTES ---
@app.route('/')
@login_required
def index():
    session = get_db_session()
    try:
        total_members = session.query(Member).count()
        total_payments = session.query(Payment).count()
        recent_payments = session.query(Payment).order_by(Payment.payment_date.desc()).limit(5).all()
        return render_template('index.html',
                               total_members=total_members,
                               total_payments=total_payments,
                               recent_payments=recent_payments)
    except SQLAlchemyError as e:
        flash(f"Database error: {str(e)}", 'error')
        return render_template('index.html',
                               total_members=0,
                               total_payments=0,
                               recent_payments=[])
    finally:
        session.close()

@app.route('/members')
@login_required
def members():
    try:
        members = get_all_members()
        return render_template('members.html', members=members)
    except Exception as e:
        flash(f"Error loading members: {str(e)}", 'error')
        return render_template('members.html', members=[])

@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member_route():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name'].strip()
            last_name = request.form['last_name'].strip()
            email = request.form['email'].strip()
            phone = request.form.get('phone', '').strip()
            membership_type = request.form.get('membership_type', 'Monthly')
            
            if not all([first_name, last_name, email]):
                flash("First name, last name, and email are required", 'error')
                return redirect(url_for('add_member_route'))
            
            success, message = add_member(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone if phone else None,
                membership_type=membership_type
            )
            
            flash(message, 'success' if success else 'error')
            return redirect(url_for('members'))
        except IntegrityError:
            flash("A member with this email already exists", 'error')
            return redirect(url_for('add_member_route'))
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
            return redirect(url_for('add_member_route'))
    
    return render_template('add_member.html')

@app.route('/members/<int:member_id>/delete', methods=['POST'])
@login_required
def delete_member_route(member_id):
    try:
        success, message = delete_member(member_id)
        flash(message, 'success' if success else 'error')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    return redirect(url_for('members'))

@app.route('/payments')
@login_required
def payments():
    try:
        payments = get_all_payments()
        return render_template('payments.html', payments=payments)
    except Exception as e:
        flash(f"Error loading payments: {str(e)}", 'error')
        return render_template('payments.html', payments=[])

@app.route('/payments/add', methods=['GET', 'POST'])
@login_required
def add_payment_route():
    if request.method == 'POST':
        try:
            member_id = int(request.form['member_id'])
            amount = float(request.form['amount'])
            payment_method = request.form['payment_method']
            
            if amount <= 0:
                flash("Amount must be positive", 'error')
                return redirect(url_for('add_payment_route'))
                
            success, message = record_payment(member_id, amount, payment_method)
            if success:
                flash(message, 'success')
                return redirect(url_for('payments'))
            else:
                flash(message, 'error')
                return redirect(url_for('add_payment_route'))
        except ValueError:
            flash("Invalid input format", 'error')
            return redirect(url_for('add_payment_route'))
        except Exception as e:
            flash(f"Error recording payment: {str(e)}", 'error')
            return redirect(url_for('add_payment_route'))
    
    try:
        members = get_all_members()
        if not members:
            flash("No members available. Please add members first.", 'warning')
            return redirect(url_for('members'))
        return render_template('add_payment.html', members=members)
    except Exception as e:
        flash(f"Error loading members: {str(e)}", 'error')
        return redirect(url_for('payments'))

@app.route('/payments/<int:payment_id>/delete', methods=['POST'])
@login_required
def delete_payment_route(payment_id):
    try:
        success, message = delete_payment(payment_id)
        flash(message, 'success' if success else 'error')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    return redirect(url_for('payments'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
