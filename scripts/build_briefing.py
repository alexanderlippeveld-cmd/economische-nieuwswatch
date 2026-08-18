#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, email.utils, hashlib, html, json, re, ssl, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc)
CUTOFF = NOW - dt.timedelta(hours=36)
UA = "EconomischeNieuwswatch/1.0 (+personal RSS reader)"

TOPICS = {
 "Macro-economie & conjunctuur": ["inflatie","groei","bbp","gdp","recessie","economie","conjunctuur","prijzen"],
 "Monetair beleid & rente": ["ecb","rente","interest","centrale bank","monetair","inflation"],
 "Beurzen & financiën": ["beurs","aandeel","obligatie","bank","markt","invest","stock","bond"],
 "Bedrijven & sectoren": ["bedrijf","sector","industrie","retail","winst","omzet","ondernem"],
 "Energie & grondstoffen": ["energie","olie","gas","elektric","grondstof","power","oil"],
 "Arbeidsmarkt & sociaal": ["werk","loon","arbeid","tewerk","werkloos","vakbond","job"],
 "Handel & geopolitiek": ["handel","tarief","export","import","sanctie","trade","china","verenigde staten"],
 "Technologie": ["technologie","ai","chip","digitaal","software","kunstmatige intelligentie"]
}

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def text(node, names):
    for child in list(node):
        tag = child.tag.split('}')[-1].lower()
        if tag in names:
            if tag == 'link' and child.attrib.get('href'): return child.attrib['href']
            return ''.join(child.itertext()).strip()
    return ''

def parse_date(value):
    if not value: return NOW
    try:
        d=email.utils.parsedate_to_datetime(value)
        return d.replace(tzinfo=d.tzinfo or dt.timezone.utc).astimezone(dt.timezone.utc)
    except Exception: pass
    try:
        return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(dt.timezone.utc)
    except Exception: return NOW

def fetch(source):
    req=urllib.request.Request(source['url'], headers={'User-Agent':UA,'Accept':'application/rss+xml, application/atom+xml, text/xml'})
    ctx=ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r: data=r.read(5_000_000)
    root=ET.fromstring(data)
    nodes=[n for n in root.iter() if n.tag.split('}')[-1].lower() in ('item','entry')]
    result=[]
    for n in nodes[:80]:
        title=clean(text(n, {'title'})); link=text(n, {'link','guid','id'})
        desc=clean(text(n, {'description','summary','content','encoded'}))
        date=parse_date(text(n, {'pubdate','published','updated','date'}))
        if not title or not link or date < CUTOFF: continue
        uid=hashlib.sha256(re.sub(r"[?#].*$", "", link).encode()).hexdigest()[:16]
        result.append({'id':uid,'title':title,'url':link,'source':source['name'],'region':source.get('region',''),
          'paywall':bool(source.get('paywall')),'published_at':date.isoformat(),'snippet':desc[:700]})
    return result

def topic_for(article):
    txt=(article['title']+' '+article['snippet']).lower()
    scores={k:sum(txt.count(word) for word in ws) for k,ws in TOPICS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best] else 'Bedrijven & sectoren'

def summary(article):
    snippet=article['snippet']
    if snippet:
        parts=re.split(r"(?<=[.!?])\s+", snippet)
        return ' '.join(parts[:2])[:420]
    return article['title']

def why(topic):
    return {
      'Macro-economie & conjunctuur':'Relevant voor koopkracht, groei en de vooruitzichten voor Belgische ondernemingen.',
      'Monetair beleid & rente':'Rente-evoluties werken door in woonkredieten, sparen, investeringen en overheidsfinanciën.',
      'Beurzen & financiën':'Marktbewegingen beïnvloeden financiering, pensioensparen en het ondernemersvertrouwen.',
      'Bedrijven & sectoren':'Geeft aan waar omzet, jobs en concurrentiedruk in de reële economie bewegen.',
      'Energie & grondstoffen':'Energieprijzen hebben snel impact op gezinnen, industrie en inflatie.',
      'Arbeidsmarkt & sociaal':'Belangrijk voor lonen, werkgelegenheid en het Belgische sociaal overleg.',
      'Handel & geopolitiek':'Open economieën zoals België voelen handels- en toeleveringsschokken relatief snel.',
      'Technologie':'Technologische verschuivingen veranderen productiviteit, investeringen en banen.'
    }[topic]

def main():
    sources=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    keywords=json.loads((ROOT/'keywords.json').read_text(encoding='utf-8'))
    articles=[]; errors=[]
    for source in sources:
        try: articles += fetch(source)
        except Exception as e:
            errors.append(f"{source['name']}: {type(e).__name__}: {e}")
    unique={a['id']:a for a in articles}
    articles=sorted(unique.values(), key=lambda a:a['published_at'], reverse=True)
    for a in articles:
        a['topic']=topic_for(a); a['summary']=summary(a); a['why']=why(a['topic'])
        hay=(a['title']+' '+a['snippet']).lower()
        a['keyword_matches']=[k for k in keywords if k.lower() in hay]
    top=[]
    seen=set()
    for a in articles:
        if a['topic'] not in seen:
            top.append(a['title']); seen.add(a['topic'])
        if len(top)==7: break
    day=NOW.date().isoformat()
    payload={'date':day,'generated_at':NOW.isoformat(),'top':top,'articles':articles,'errors':errors,
             'stats':{'articles':len(articles),'sources_ok':len(sources)-len(errors),'sources_total':len(sources)}}
    (OUT/f'{day}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'briefing.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    archive=[]
    for p in sorted(OUT.glob('20??-??-??.json'), reverse=True)[:90]:
        try:
            x=json.loads(p.read_text(encoding='utf-8')); archive.append({'date':x['date'],'articles':len(x['articles'])})
        except Exception: pass
    (OUT/'archive.json').write_text(json.dumps(archive,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"{len(articles)} artikels, {len(errors)} feedfouten")
    for e in errors: print('WAARSCHUWING',e)
if __name__=='__main__': main()
