import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from processor import VideoProcessor
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
# In a real app, this should be a secure random string
app.secret_key = 'supersecretkey_for_demo_purposes'

# Configure Upload Folder
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'flask_uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Dummy User Database for MVP
USERS = {
    "admin": "password123",
    "player": "cricket"
}

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    if 'video' not in request.files:
        flash('No video file uploaded', 'error')
        return redirect(url_for('dashboard'))
        
    file = request.files['video']
    player_name = request.form.get('player_name', 'Player')
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard'))
        
    if file:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Output path
        output_filename = f"analyzed_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        try:
            # Analyze
            processor = VideoProcessor()
            processor.process_video(input_path, output_path, player_name=player_name)
            
            # For this MVP, we'll just send the file back directly or show it.
            # Ideally, we serve it via a static route or send_file
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        except Exception as e:
            flash(f'Error processing video: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
