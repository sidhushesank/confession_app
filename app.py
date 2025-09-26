from flask import Flask, render_template, request, flash, send_file, abort
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages

@app.route('/', methods=['GET', 'POST'])
def confess():
    if request.method == 'POST':
        ig_username = request.form.get('ig_username', '').strip()
        confession = request.form.get('confession', '').strip()

        if not ig_username:
            flash('Instagram username is required to submit a confession.')
            return render_template('confession.html', ig_username=ig_username, confession=confession)

        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        timestamp = datetime.datetime.now()
        with open('data/confessions.txt', 'a') as f:
            f.write(f"{timestamp} | {ig_username} | {ip} | {user_agent} | {confession}\n")

        return render_template('submitted.html')

    return render_template('confession.html')

@app.route('/download-confessions')
def download_confessions():
    # Simple security key check to prevent unauthorized download
    secret_key = request.args.get('key')
    if secret_key != 'admin123':  # Change 'YOUR_SECRET_KEY' to a strong password
        abort(403)  # Forbidden access otherwise

    try:
        return send_file('data/confessions.txt', as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
