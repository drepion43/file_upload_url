from flask import Flask, request, render_template_string, send_from_directory, abort
from werkzeug.utils import secure_filename
import os

BASE_UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

UPLOAD_FORM = '''
<!doctype html>
<title>Upload File</title>
<h1>Upload a File to "{{ category }}/{{ subdir }}"</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
'''

@app.route('/upload/<category>/<subdir>', methods=['GET', 'POST'])
def upload_file(category, subdir):
    category = secure_filename(category)
    subdir = secure_filename(subdir)
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], category, subdir)
    ensure_dir(upload_dir)

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            download_url = f'/download/{category}/{subdir}/{filename}'
            return f'''
                File uploaded: <a href="{download_url}">{filename}</a><br>
                <a href="/upload/{category}/{subdir}">Upload another</a>
            '''
        return 'Invalid file', 400
    return render_template_string(UPLOAD_FORM, category=category, subdir=subdir)

@app.route('/download/<category>/<subdir>/<filename>')
def download_file(category, subdir, filename):
    category = secure_filename(category)
    subdir = secure_filename(subdir)
    filename = secure_filename(filename)
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], category, subdir)
    filepath = os.path.join(upload_dir, filename)
    if not os.path.exists(filepath):
        abort(404)
    return send_from_directory(upload_dir, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)