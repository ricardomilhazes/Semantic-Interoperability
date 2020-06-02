import requests
import json
import textwrap
from app.config import SCOPUS_API_KEY
from datetime import datetime

def s(texto_):
    return "'" + texto_.replace("'"," ") + "'"
    
def get_scopus_info(SCOPUS_ID):
    url = ("http://api.elsevier.com/content/abstract/scopus_id/"
          + SCOPUS_ID
          + "?field=authors,title,publicationName,volume,issueIdentifier,"
          + "prism:pageRange,coverDate,article-number,doi,citedby-count,prism:aggregationType")
    
    resp = requests.get(url,headers={'Accept':'application/json','X-ELS-APIKey': SCOPUS_API_KEY})

    if resp.status_code > 400:
        return '', '', '', ''

    results = json.loads(resp.text.encode('utf-8'))

    authors = ', '.join([au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']])
    title = results['abstracts-retrieval-response']['coredata']['dc:title']

    date = results['abstracts-retrieval-response']['coredata']['prism:coverDate']
    dt = datetime.strptime(date, '%Y-%m-%d')

    cites = int(results['abstracts-retrieval-response']['coredata']['citedby-count'].encode('utf-8'))
    
    return authors, title, dt, cites

def get_orcid_ids(ORCID_ID_):
    resp = requests.get("https://pub.orcid.org/v3.0/"+ORCID_ID_+"/works",
                    headers={'Accept':'application/json'})

    if resp.status_code > 400:
        return None
    
    results = resp.json()
    my_list = []

    investigator_document = {
        'orcid_id' : ORCID_ID_,
        'last_updated' : datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
    }

    name = results['group'][0]['work-summary'][0]['source']['assertion-origin-name']['value']
    investigator_document['name'] = name

    for r in results['group']:
        for r2 in r['work-summary']:
            try:
                my_list.append(r2['url']['value'])
                type_ = r2['type']
            except:
                my_list.append('None')

    publications = []

    info = {
                "title" : '',
                "year" : '',
                "local" : '',
                "scopus": {
                    "eid" : '',
                    "type" : '',
                    "authors" : '',
                    "num_quotes" : '',
                    "sjr" : '',
                },
                "webofscience": {
                    "wos" : '',
                    "type" : ''
                }
            }

    my_list2 = []
    
    print("mylist:",len(my_list))
    for r in my_list:
        print("r:",r)
        info["scopus"]["type"] = type_
        if r.find('eid=') > 0:
            k1 = r.find('eid=')
            k2 = r.find('&',k1)
            if r[k1+11:k2] not in my_list2:
                eid = (r[k1+11:k2])
                authors, title, dt, cites = get_scopus_info(eid)
                info["title"] = title
                info["year"] = dt.year
                info["scopus"]["eid"] = eid
                info["scopus"]["authors"] = authors
                info["scopus"]["num_quotes"] = cites
                publications.append(info)
                my_list2.append(r[k1+11:k2])

    investigator_document["publications"] = publications

    print(investigator_document)
    return investigator_document

# get_orcid_ids('0000-0003-4121-6169')