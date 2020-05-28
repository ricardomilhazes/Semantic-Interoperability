from app import app
from flask import render_template, request, redirect, url_for
from app.models import get_profile

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        result = request.form
        return redirect(url_for('search', ids=result['ids']))
    else:
        return render_template('index.html')

@app.route('/search/<ids>')
def search(ids):
    print("GET", ids)
    to_search = ids.split(',')
    to_search = [id.strip() for id in to_search]
    print(to_search)
    profiles = []
    for id in to_search:
        profile = get_profile(id)
        if profile is None:
            # fazer pedido à API
            print("não tenho na BD, vou buscar à API")
            # se for chamado com sucesso a API:
            # profiles.append(new_profile)
            # se der erro:
            profiles.append({
                'id': id,
                'error': 'Something went wrong.'
            })
        else:
            profiles.append(profile)
    return render_template('profile.html', profiles=profiles)