import requests
import json
import textwrap
from app.config import SCOPUS_API_KEY
from datetime import datetime
import time
import random
import concurrent.futures

CONNECTIONS = 5
TIMEOUT = 5

def s(texto_):
    return "'" + texto_.replace("'"," ") + "'"
    
def get_scopus_info(SCOPUS_ID):
    # sleep randomly between 0 and 2 secs in order to not get 429: TOO MANY REQUESTS
    time.sleep(random.randint(0,2))

    url = ("http://api.elsevier.com/content/abstract/scopus_id/"
          + SCOPUS_ID
          + "?field=authors,title,publicationName,volume,issueIdentifier,"
          + "prism:pageRange,coverDate,article-number,doi,citedby-count,prism:aggregationType")
    
    resp = requests.get(url,headers={'Accept':'application/json','X-ELS-APIKey': SCOPUS_API_KEY})

    if resp.status_code > 400:
        print(resp.status_code)
        return SCOPUS_ID, '', -1

    results = json.loads(resp.text.encode('utf-8'))

    authors = ', '.join([au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']])
    # title = results['abstracts-retrieval-response']['coredata']['dc:title']

    # date = results['abstracts-retrieval-response']['coredata']['prism:coverDate']
    # dt = datetime.strptime(date, '%Y-%m-%d')

    cites = int(results['abstracts-retrieval-response']['coredata']['citedby-count'].encode('utf-8'))
    
    # return authors, title, dt, cites
    return SCOPUS_ID, authors, cites

def get_personal_info(ORCID_ID):
    person = requests.get("https://pub.orcid.org/v3.0/"+ORCID_ID+'/person',
                    headers={'Accept':'application/json'})

    if person.status_code > 400:
        return None
    
    return person.json()

def get_works(ORCID_ID):
    works = requests.get("https://pub.orcid.org/v3.0/"+ORCID_ID+'/works',
                    headers={'Accept':'application/json'})

    if works.status_code > 400:
        return None
    
    return works.json()

def get_infos(ORCID_ID):
    time1 = time.time()

    # request the ORCID API the authors personal info
    personal_info = get_personal_info(ORCID_ID)
    if personal_info:
        name = personal_info['name']['credit-name']['value']
    else:
        return None

    # init result dict
    investigator_document = {
        'orcid_id' : ORCID_ID,
        'last_updated' : datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        'name': name
    }

    # request the ORCID API the authors works
    works = get_works(ORCID_ID)

    # print("WORKS:", works)
    with open('works.json', 'w', encoding='utf-8') as f:
        json.dump(works, f, ensure_ascii=False, indent=4)

    pubs = []
    titles = []
    eids = []
    # iterate over publications group
    for work in works['group']:
        # iterate over work summary
        for summary in work['work-summary']:
            pub = {}
            # get publication type
            pub['title'] = summary['title']['title']['value']
            # if publication is not already in the array
            if pub['title'].lower() not in titles:
                # get year
                pub['year'] = summary['publication-date']['year']['value']
                # get publication type
                pub['type'] = summary['type']
                
                # if it has the name of the journal, add it to the object
                if summary['journal-title'] is not None:
                    pub['local'] = summary['journal-title']['value']
                
                has_eid = False
                # check external ids
                if 'external-ids' in summary:
                    if summary['external-ids'] is not None:
                        for external_id in summary['external-ids']['external-id']:
                                # if has eid, then gonna need to fetch Scopus Infos
                                if external_id['external-id-type'] == 'eid':
                                    pub['scopus'] = {}
                                    pub['scopus']['eid'] = external_id['external-id-value'][7:]
                                    eids.append(pub['scopus']['eid'])
                                    has_eid = True

                                # if has wosuid, then add WOS ID to the publication info
                                if external_id['external-id-type'] == 'wosuid':
                                    pub['webofscience'] = {}
                                    pub['webofscience']['wos'] = external_id['external-id-value']
                
                if not has_eid:
                    eids.append(-1)
                pubs.append(pub)
                titles.append(pub['title'].lower())
            
    print("pubs:", len(pubs))
    print("eids:", len(eids))

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = (executor.submit(get_scopus_info, eid) for eid in [val for val in eids if val!=-1])
        for future in concurrent.futures.as_completed(future_to_url):
            eid, authors, cites = future.result(timeout=TIMEOUT)
            # print(eid, authors, cites)
            idx = eids.index(eid)
            if idx:
                if authors is not None and 'scopus' in pubs[idx]:
                    pubs[idx]['scopus']['authors'] = authors
                if cites is not None and 'scopus' in pubs[idx]:
                    pubs[idx]['scopus']['num_quotes'] = cites

        time2 = time.time()
        totalTime = time2 - time1
        print("time:", totalTime)

    investigator_document["publications"] = pubs

    with open('machado.json', 'w', encoding='utf-8') as f:
        json.dump(investigator_document, f, ensure_ascii=False, indent=4)

    return totalTime, investigator_document


    # for r in results['group']:
    #     for r2 in r['work-summary']:
    #         try:
    #             my_list.append(r2['url']['value'])
    #             type_ = r2['type']
    #         except:
    #             my_list.append('None')

    # publications = []

    # info = {
    #             "title" : '',
    #             "year" : '',
    #             "local" : '',
    #             "scopus": {
    #                 "eid" : '',
    #                 "type" : '',
    #                 "authors" : '',
    #                 "num_quotes" : '',
    #                 "sjr" : '',
    #             },
    #             "webofscience": {
    #                 "wos" : '',
    #                 "type" : ''
    #             }
    #         }

    # my_list2 = []
    
    # print("mylist:",len(my_list))
    # for r in my_list:
    #     print("r:",r)
    #     info["scopus"]["type"] = type_
    #     if r.find('eid=') > 0:
    #         k1 = r.find('eid=')
    #         k2 = r.find('&',k1)
    #         if r[k1+11:k2] not in my_list2:
    #             eid = (r[k1+11:k2])
    #             authors, title, dt, cites = get_scopus_info(eid)
    #             info["title"] = title
    #             info["year"] = dt.year
    #             info["scopus"]["eid"] = eid
    #             info["scopus"]["authors"] = authors
    #             info["scopus"]["num_quotes"] = cites
    #             publications.append(info)
    #             my_list2.append(r[k1+11:k2])

    # 

    # print(investigator_document)
    # return investigator_document

# get_infos('0000-0003-4121-6169')