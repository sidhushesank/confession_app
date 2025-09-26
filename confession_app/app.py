from flask import Flask, render_template, request, flash
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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

if __name__ == '__main__':
    app.run(debug=True)
