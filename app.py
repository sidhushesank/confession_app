import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.secret_key = 'supersecretkey_change_this_to_random_string'

# MongoDB Connection
# MongoDB Connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://confession_admin:RJj2aBtLdtndFITX@cluster0.idcdq9o.mongodb.net/?appName=Cluster0')

client = None
db = None
confessions_collection = None

try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client['confession_db']
    confessions_collection = db['confessions']
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection error: {e}")

# Admin secret key
ADMIN_KEY = 'admin123'


@app.route('/')
def index():
    return render_template('confession.html')


@app.route('/submit', methods=['POST'])
def submit():
    confession = request.form.get('confession', '').strip()
    ig_username = request.form.get('ig_username', '').strip()
    
    if not confession:
        flash('Confession cannot be empty!', 'error')
        return redirect(url_for('index'))
    
    # Get metadata
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    timestamp = datetime.now()
    username_display = ig_username if ig_username else "Anonymous"
    
    # Create confession document
    confession_doc = {
        'timestamp': timestamp,
        'username': username_display,
        'ip': ip,
        'user_agent': user_agent,
        'confession': confession
    }
    
    try:
        # Insert into MongoDB
        confessions_collection.insert_one(confession_doc)
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
        # Fetch all confessions from MongoDB (sorted by newest first)
        confessions_cursor = confessions_collection.find().sort('timestamp', -1)
        
        # Format confessions for display
        confessions = []
        for doc in confessions_cursor:
            timestamp_str = doc['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            confession_entry = f"[{timestamp_str}] @{doc['username']} | IP: {doc['ip']} | {doc['confession']}"
            confessions.append(confession_entry)
        
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
        # Fetch all confessions
        confessions_cursor = confessions_collection.find().sort('timestamp', -1)
        
        # Format for download
        confession_lines = []
        for doc in confessions_cursor:
            timestamp_str = doc['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            line = f"[{timestamp_str}] @{doc['username']} | IP: {doc['ip']} | {doc['confession']}"
            confession_lines.append(line)
        
        content = '\n'.join(confession_lines) if confession_lines else "No confessions yet!"
        
        return Response(
            content,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment;filename=confessions.txt'}
        )
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)
