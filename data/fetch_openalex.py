"""Download counts of research articles by country and year from OpenAlex.
Run on your own computer (Python 3, no extra packages):

    export OPENALEX_API_KEY=your_key        (Windows PowerShell:  $env:OPENALEX_API_KEY="your_key")
    python fetch_openalex.py

Writes openalex_articles_by_country_year.csv and openalex_fetch_log.json next to this script.
A work with authors in several countries is counted once for each of those countries."""
import os, sys, json, time, csv, datetime, urllib.request, urllib.parse, urllib.error
KEY=os.environ.get('OPENALEX_API_KEY')
if not KEY: sys.exit("Set OPENALEX_API_KEY first (see the top of this file).")
BASE="https://api.openalex.org/works"; Y0,Y1=1950,2023
def get(params):
    params=dict(params,api_key=KEY); url=BASE+"?"+urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url,timeout=60) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503,504): time.sleep(5*(attempt+1)); continue
            sys.exit("OpenAlex refused the request (HTTP %d): %s"%(e.code,e.read().decode()[:300]))
        except Exception as e: time.sleep(5*(attempt+1))
    sys.exit("Gave up after repeated failures: "+url.replace(KEY,'***'))
base_filter="type:article,publication_year:%d-%d"%(Y0,Y1)
# 1. which country codes exist (largest 200 by article count)
g=get({"filter":base_filter,"group_by":"authorships.institutions.country_code"})["group_by"]
codes=[x["key"].split("/")[-1].upper() for x in g if x["key"] and x["key"].lower()!="unknown"]
print("countries:",len(codes))
rows=[]; world=get({"filter":base_filter,"group_by":"publication_year"})["group_by"]
rows+=[("WORLD",int(x["key"]),x["count"]) for x in world]
for i,c in enumerate(codes):
    r=get({"filter":base_filter+",authorships.institutions.country_code:"+c,"group_by":"publication_year"})["group_by"]
    rows+=[(c,int(x["key"]),x["count"]) for x in r]; print("%3d/%d %s %d years"%(i+1,len(codes),c,len(r))); time.sleep(0.15)
here=os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here,"openalex_articles_by_country_year.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["country_iso2","year","articles"]); w.writerows(sorted(rows))
json.dump(dict(fetched=datetime.datetime.utcnow().isoformat()+"Z",endpoint=BASE,filter=base_filter,group_by="publication_year per authorships.institutions.country_code",
               countries=len(codes),rows=len(rows),note="WORLD = all articles regardless of affiliation; articles with no country affiliation appear only there"),
          open(os.path.join(here,"openalex_fetch_log.json"),"w"),indent=1)
print("done:",len(rows),"rows")
