import requests
import json
import textwrap
import config

def s(texto_):
    return "'" + texto_.replace("'"," ") + "'"
    
def get_scopus_info(SCOPUS_ID):
    url = ("http://api.elsevier.com/content/abstract/scopus_id/"+ SCOPUS_ID
        + "?field=authors,title,publicationName,volume,issueIdentifier,"
        + "prism:pageRange,coverDate,article-number,doi,issn,citedby-count,prism:aggregationType")
    
    resp = requests.get(url,headers={'Accept':'application/json','X-ELS-APIKey': config.SCOPUS_API_KEY})
    
    return json.loads(resp.text.encode('utf-8'))

def get_orcid_ids(ORCID_ID_):
    resp = requests.get("https://pub.orcid.org/v3.0/"+ORCID_ID_+"/works",
                    headers={'Accept':'application/json'})
    
    results = resp.json()
    my_list = []
    
    for r in results['group']:
        for r2 in r['work-summary']:
            try:
                my_list.append(r2['url']['value'])
            except:
                my_list.append('None')
    
    my_list2 = []
    
    for r in my_list:
        if r.find('eid=') > 0:
            k1 = r.find('eid=')
            k2 = r.find('&',k1)
            if r[k1+11:k2] not in my_list2:
                my_list2.append(r[k1+11:k2])
    
    return my_list2

orcids_ids = get_orcid_ids('0000-0003-4121-6169')

for id in orcids_ids:
    print(get_scopus_info(id))