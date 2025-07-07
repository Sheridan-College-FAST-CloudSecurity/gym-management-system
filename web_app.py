from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from gym_manager.database import get_db_session, Member, Payment
from gym_manager.members import add_member, get_all_members, get_member_by_id, delete_member
from gym_manager.payments import record_payment, get_payments_by_member, get_all_payments, delete_payment
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "your_secret_key_here"

def calculate_membership_fee(membership_type, months):
    """Calculate membership fee based on type and duration"""
    rates = {"Monthly": 30, "Quarterly": 80, "Annual": 300}
    return rates.get(membership_type, 0)

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

# ============= ORIGINAL ROUTES (COMPLETELY UNCHANGED) =============

@app.route('/')
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
def members():
    try:
        members = get_all_members()
        return render_template('members.html', members=members)
    except Exception as e:
        flash(f"Error loading members: {str(e)}", 'error')
        return render_template('members.html', members=[])

@app.route('/members/add', methods=['GET', 'POST'])
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

@app.route('/members/<int:member_id>/delete')
def delete_member_route(member_id):
    try:
        success, message = delete_member(member_id)
        flash(message, 'success' if success else 'error')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    return redirect(url_for('members'))

@app.route('/payments')
def payments():
    try:
        payments = get_all_payments()
        return render_template('payments.html', payments=payments)
    except Exception as e:
        flash(f"Error loading payments: {str(e)}", 'error')
        return render_template('payments.html', payments=[])

@app.route('/payments/add', methods=['GET', 'POST'])
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
def delete_payment_route(payment_id):
    try:
        success, message = delete_payment(payment_id)
        flash(message, 'success' if success else 'error')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    return redirect(url_for('payments'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)