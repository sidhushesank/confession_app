import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey_change_this'  # Change this!

# Config
UPLOAD_FOLDER = 'data'
CONFESSIONS_FILE = os.path.join(UPLOAD_FOLDER, 'confessions.txt')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Admin secret key
ADMIN_KEY = 'admin123'  # Change this!


@app.route('/')
def index():
    return render_template('confession.html')


@app.route('/submit', methods=['POST'])
def submit():
    confession = request.form.get('confession', '').strip()
    ig_username = request.form.get('ig_username', '').strip()  # OPTIONAL now!
    
    if not confession:
        flash('Confession cannot be empty!', 'error')
        return redirect(url_for('index'))
    
    # Get metadata (for admin tracking, NOT shown to users)
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Format: Show "Anonymous" if no Instagram username provided
    username_display = ig_username if ig_username else "Anonymous"
    
    # Save confession with all details
    confession_entry = f"[{timestamp}] @{username_display} | IP: {ip} | {confession}\n"
    
    try:
        with open(CONFESSIONS_FILE, 'a', encoding='utf-8') as f:
            f.write(confession_entry)
        return render_template('submitted.html')
    except Exception as e:
        flash(f'Error saving confession: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/view-confessions')
def view_confessions():
    """View all confessions in browser (admin only)"""
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    try:
        if os.path.exists(CONFESSIONS_FILE):
            with open(CONFESSIONS_FILE, 'r', encoding='utf-8') as f:
                confessions = f.readlines()
        else:
            confessions = []
        
        return render_template('view_confessions.html', confessions=confessions)
    except Exception as e:
        return f"Error reading confessions: {str(e)}", 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        entered_key = request.form.get('key', '')
        
        if entered_key == ADMIN_KEY:
            session['authenticated'] = True
            return redirect(url_for('view_confessions'))
        else:
            flash('Invalid secret key!', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.pop('authenticated', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/download-confessions')
def download_confessions():
    """Download confessions file (admin only)"""
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    try:
        if os.path.exists(CONFESSIONS_FILE):
            with open(CONFESSIONS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            return Response(
                content,
                mimetype='text/plain',
                headers={'Content-Disposition': 'attachment;filename=confessions.txt'}
            )
        else:
            return "No confessions yet!", 404
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)
