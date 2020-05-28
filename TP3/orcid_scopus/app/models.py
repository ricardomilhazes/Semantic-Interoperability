# DB MODEL:

# investigator document:
# {
#   id,
#   orcid_id,
#   last_updated,
#   name,
#   publications: [
#       {
#           title,
#           year,
#           local,
#           scopus: {
#               eid,
#               type (null),
#               authors,
#               num_quotes,
#               num_quotes_last_three_years,
#               sjr 
#           }
#           webofscience: {
#               wos,
#               type (null)
#           }
#       }
#   ]
# }

from app import mongo

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