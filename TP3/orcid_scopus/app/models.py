# DB MODEL:

# investigator document:
# {
#   _id,
#   orcid_id,
#   last_updated,
#   name,
#   publications: [
#       {
#           title,
#           year,
#           local,
#           type
#           scopus: {
#               eid,
#               authors,
#               num_quotes,
#               sjr 
#           }
#           webofscience: {
#               wos,
#           }
#       }
#   ]
# }

from app import mongo
from app.collector import get_infos

# Get investigator with orcid_id "id"
def get_profile(id):
    # WE NEED TO CHECK BEFORE IF DB IS NOT NONE
    if mongo.db is not None:
        profile = mongo.db.investigators.find_one({"orcid_id": id})
        return profile
    else:
        return None

def update_profile(id, data):
    if mongo.db is not None:
        #  upsert false pq n queremos criar novo se n existir
        mongo.db.investigators.update_one({'orcid_id': id}, {"$set": data}, upsert=False)

def insert_profile(data):
    if mongo.db is not None:
        #  insert new document aka python dict
        mongo.db.investigators.insert_one(data)

def update_all():
    if mongo.db is not None:
        all_profiles = mongo.db.investigators.find()
        for profile in all_profiles:
            id = profile['orcid_id']
            print("vou buscar infos", id)
            new_info = get_infos(id)
            if new_info != profile:
                print("é diferente do q o que tenho, vou atualizar BD")
                update_profile(id, new_info)
            else:
                print("igual, nao ha updates", id)
    return len(all_profiles)

def insert_benchmark(data):
    if mongo.db is not None:
        #  insert new document aka python dict
        mongo.db.benchmarking.insert_one(data)

def get_api_benchmark():
    if mongo.db is not None:
        return mongo.db.benchmarking.find({'type': 'api'})
    else:
        return None

def get_db_benchmark():
    if mongo.db is not None:
        return mongo.db.benchmarking.find({'type': 'db'})
    else:
        return None

def get_weekly_updates_benchmark():
    if mongo.db is not None:
        return mongo.db.benchmarking.find({'type': 'update'})
    else:
        return None

def get_values(list):
    res = {}
    for doc in list:
        num_pubs = doc['num_pubs']
        if num_pubs in res:
            res[num_pubs]['times'].append(doc['time'])
            res[num_pubs]['time_average'] = sum(res[num_pubs]['times']) / len(res[num_pubs]['times'])
            if 'errors' in doc:
                res[num_pubs]['errors'].append(doc['errors'])
                res[num_pubs]['error_average'] = ( sum(res[num_pubs]['errors']) / len(res[num_pubs]['errors']) ) / num_pubs
        else:
            res[num_pubs] = {}
            res[num_pubs]['times'] = []
            res[num_pubs]['times'].append(doc['time'])
            res[num_pubs]['time_average'] = 0
            res[num_pubs]['time_average'] = sum(res[num_pubs]['times']) / len(res[num_pubs]['times'])
            if 'errors' in doc:
                res[num_pubs]['errors'] = []
                res[num_pubs]['errors'].append(doc['errors'])
                res[num_pubs]['error_average'] = 0
                res[num_pubs]['error_average'] = ( sum(res[num_pubs]['errors']) / len(res[num_pubs]['errors']) ) / num_pubs
    return res