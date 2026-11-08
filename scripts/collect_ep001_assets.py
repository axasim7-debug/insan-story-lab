from pathlib import Path
import urllib.request, urllib.parse, json, hashlib, concurrent.futures, re
r=Path(__file__).resolve().parents[1]/'episodes/EP001/assets'
for d in ['research','reference','licensed','evidence']: (r/d).mkdir(exist_ok=True)
items=[
('pdf-precup','research/precup-memory-paper.pdf','https://ubr.rev.unibuc.ro/wp-content/uploads/2014/12/MihaelaPrecup.pdf','pdf'),
('audio-heller-1','reference/heller-interview-part1.mp3','https://www.tvtimemachine.com/sys/wp-content/uploads/2012/01/TheMentalistSegment1Web.mp3','audio'),
('audio-heller-2','reference/heller-interview-part2.mp3','https://www.tvtimemachine.com/sys/wp-content/uploads/2012/01/TheMentalistSegment2Web.mp3','audio'),
('audio-heller-3','reference/heller-interview-part3.mp3','https://www.tvtimemachine.com/sys/wp-content/uploads/2012/01/TheMentalistSegment3Web.mp3','audio'),
('pdf-revenge','research/carlsmith-revenge-2008.pdf','https://dtg.sites.fas.harvard.edu/CARLSMITH%2C%20WILSON%2C%20%26%20GILBERT%20%282008%29.pdf','pdf'),
('pdf-bias','research/west-bias-blind-spot-2012.pdf','https://www.keithstanovich.com/Site/Research_on_Reasoning_files/West_Stanovich_JPSP2012.pdf','pdf'),
('page-heller-radio','evidence/heller-radio.html','https://www.tvtimemachine.com/1333/interview-with-the-mentalist-creator-bruno-heller','html'),
('page-heller-tvguide','evidence/heller-tvguide.html','https://www.tvguide.com/news/mentalist-bruno-heller-season-6-premiere-1071429/','html'),
('page-baker-digitalspy','evidence/baker-digitalspy.html','https://www.digitalspy.com/tv/a150413/simon-baker-the-mentalist/','html'),
('photo-baker-license','evidence/baker-commons-license.html','https://commons.wikimedia.org/wiki/File:Simon_Baker_on_set.jpg','html'),
('photo-car-license','evidence/car-commons-license.html',"https://commons.wikimedia.org/wiki/File:Citro%C3%ABn_DS_20_Pallas_1973_-_Mondial_de_l%27Automobile_de_Paris_2016_-_001.jpg",'html')]
def fetch(item):
 id,path,url,kind=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'ChannelResearch/1.0 research source archiving'})
  with urllib.request.urlopen(req,timeout=35) as q:
   data=q.read(35*1024*1024);ctype=q.headers.get('Content-Type','');final=q.url
  if kind=='pdf' and not data.startswith(b'%PDF'): raise ValueError('not a PDF: '+ctype)
  if kind=='audio' and not ('audio' in ctype or data.startswith(b'ID3')): raise ValueError('not audio: '+ctype)
  p=r/path;p.write_bytes(data)
  return dict(id=id,path=str(p.relative_to(r)),url=url,final_url=final,bytes=len(data),content_type=ctype,sha256=hashlib.sha256(data).hexdigest(),status='downloaded')
 except Exception as e: return dict(id=id,url=url,status='failed',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: out=list(pool.map(fetch,items))
for name,path in [('baker','evidence/baker-commons-license.html'),('car','evidence/car-commons-license.html')]:
 p=r/path
 if p.exists():
  s=p.read_text();m=re.search(r'<a[^>]+href="(https://upload.wikimedia.org/[^\"]+)"[^>]*>Original file',s)
  if not m: m=re.search(r'class="fullImageLink"[^>]*>\s*<a href="([^\"]+)"',s)
  if m:
   url=m.group(1).replace('&amp;','&');out.append(fetch(('photo-'+name,'licensed/'+name+'.jpg',url,'image')))
  else:out.append(dict(id='photo-'+name,status='failed',error='original image link not found'))
(r/'DOWNLOAD_LOG.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for x in out:print(json.dumps({k:v for k,v in x.items() if k not in ['sha256']},ensure_ascii=False))
