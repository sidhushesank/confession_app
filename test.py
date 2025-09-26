import os

# Define folders to create
folders = [
    'confession_app',
    'confession_app/templates',
    'confession_app/static',
    'confession_app/data'
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create app.py file
app_py_content = '''from flask import Flask, render_template, request
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def confess():
    if request.method == 'POST':
        confession = request.form['confession']
        ig_username = request.form['ig_username']
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        timestamp = datetime.datetime.now()
        with open('confession_app/data/confessions.txt', 'a') as f:
            f.write(f"{timestamp} | {ig_username} | {ip} | {user_agent} | {confession}\\n")
        return "Confession submitted! Thank you."
    return render_template('confession.html')

if __name__ == '__main__':
    app.run(debug=True)
'''

with open('confession_app/app.py', 'w') as file:
    file.write(app_py_content)

# Create confession.html file
confession_html_content = '''<!DOCTYPE html>
<html>
<head><title>Confession Form</title></head>
<body>
    <h2>Send your confession anonymously</h2>
    <form method="POST">
        <input type="text" name="ig_username" placeholder="Instagram Username" required><br>
        <textarea name="confession" rows="5" cols="40" placeholder="Type your confession"></textarea><br>
        <input type="submit" value="Submit">
    </form>
    <p style="color:gray; font-size:small;">Your confession will be kept confidential. Instagram username is required for validation.</p>
</body>
</html>
'''

with open('confession_app/templates/confession.html', 'w') as file:
    file.write(confession_html_content)

# Create empty confessions.txt file
open('confession_app/data/confessions.txt', 'w').close()

print("Folder structure and files created successfully.")
