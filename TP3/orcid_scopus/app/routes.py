from app import app, scheduler
from flask import render_template, request, redirect, url_for
from app.models import get_profile, insert_profile, update_all, insert_benchmark, get_api_benchmark, get_db_benchmark, get_weekly_updates_benchmark, get_values
from app.collector import get_infos
import time

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
        time1 = time.time()
        profile = get_profile(id)
        if profile is None:
            # fazer pedido à API
            print("não tenho na BD, vou buscar à API")
            apiRetrieval, new_profile, errors = get_infos(id)

            # se for chamado com sucesso a API:
            if new_profile:
                profiles.append(new_profile)
                insert_profile(new_profile)

                if 'publications' in new_profile:
                    num_pubs = len(new_profile['publications'])

                benchmarking_db_data = {
                    'type' : 'api',
                    'time' : apiRetrieval,
                    'num_pubs' : num_pubs,
                    'errors': errors
                }

                insert_benchmark(benchmarking_db_data)
                
            # se der erro:
            else:
                profiles.append({
                    'id': id,
                    'error': 'Something went wrong.'
                })
        else:
            dbRetrieval = time.time() - time1
            print("tenho na db")

            if 'publications' in profile:
                num_pubs = len(profile['publications'])
            
            benchmarking_db_data = {
                'type' : 'db',
                'time' : dbRetrieval,
                'num_pubs' : num_pubs
            }

            insert_benchmark(benchmarking_db_data)
            profiles.append(profile)
            
    return render_template('profile.html', profiles=profiles)

@app.route('/benchmarking')
def benchmarking():
    api_docs = get_api_benchmark()
    db_docs = get_db_benchmark()
    # update_docs = get_weekly_updates_benchmark()

    api_values = get_values(api_docs)
    db_values = get_values(db_docs)
    # update_values = {}

    api_labels = api_values.keys()
    api_times = [api_values[label]['time_average'] for label in api_labels]
    api_errors = [api_values[label]['error_average'] for label in api_labels]

    print("API:", api_labels, api_times, api_errors)

    db_labels = db_values.keys()
    db_times = [db_values[label]['time_average'] for label in db_labels]

    print("DB:", db_labels, db_times)

    return render_template('benchmarking.html')


# every sunday at midnight (while the server is running) this task will be run in background
@scheduler.task('cron', id='scheduled_task', day_of_week='sun', hour=0)
def update_profiles():
    print('Scheduled Task now running')
    # time1 = time.time()
    num_invs = update_all()
    # time2 = time.time()

    # updateBenchmark = time2 - time1

    # benchmarking_db_data = {
    #     'type': 'update',
    #     'time' : updateBenchmark,
    #     'num_invs' : num_invs
    # }

    # insert_benchmark(benchmarking_db_data)

    print('Scheduled Task done!')