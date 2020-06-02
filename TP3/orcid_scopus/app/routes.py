from app import app
from flask import render_template, request, redirect, url_for
from app.models import get_profile, insert_profile
from app.collector import get_orcid_ids

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
            new_profile = get_orcid_ids(id)
            # se for chamado com sucesso a API:
            if new_profile:
                profiles.append(new_profile)
                insert_profile(new_profile)
            # se der erro:
            else:
                profiles.append({
                    'id': id,
                    'error': 'Something went wrong.'
                })
        else:
            print("tenho na db")
            profiles.append(profile)
    return render_template('profile.html', profiles=profiles)