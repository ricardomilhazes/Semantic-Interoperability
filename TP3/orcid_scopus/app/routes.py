from app import app
from flask import render_template, request

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile', methods = ['POST', 'GET'])
def get_profile():
    if request.method == 'POST':
        result = request.form
        return render_template('profile.html', ORCID_ID=result['ORCID_ID'])