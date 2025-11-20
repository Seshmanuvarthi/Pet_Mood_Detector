from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from translator import analyze_pet_mood

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return redirect(request.url)
    file = request.files['video']
    pet_type = request.form.get('pet_type')
    if file.filename == '' or not pet_type:
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            result = analyze_pet_mood(pet_type, filepath)
            # Clean up uploaded file
            os.remove(filepath)
            return render_template('result.html', result=result, pet_type=pet_type)
        except Exception as e:
            # Clean up on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('result.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
