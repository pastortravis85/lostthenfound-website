from pathlib import Path
import json,re,html,shutil
import yaml,mistune
root=Path(__file__).parent
out=root/'public';out.mkdir(exist_ok=True)
def entries(folder):
 result=[]
 for p in sorted((root/'content'/folder).glob('*.md')):
  s=p.read_text(encoding='utf8')
  if not s.startswith('---'):continue
  parts=s.split('---',2)
  if len(parts)<3:continue
  d=yaml.safe_load(parts[1]) or {}
  d['body']=parts[2].strip();d['slug']=p.stem
  result.append(d)
 return result
books=entries('devotionals');resources=entries('pastor-resources');posts=[p for p in entries('journal') if p.get('published') is True]
settings=json.loads((root/'content/site.json').read_text())
def media_url(value):
 """Normalize CMS media paths to the public /media directory."""
 if isinstance(value,dict):
  value=value.get('src') or value.get('path') or value.get('url') or ''
 value=str(value or '').strip()
 if not value:return ''
 if value.startswith(('https://','http://')):return value
 value='/' + value.lstrip('/')
 return value

s=(root/'template.html').read_text()
# Original presentation is preserved; replace hardcoded sample collections with CMS data.
s=re.sub(r'const books=\[.*?\];function bookCard', 'const books='+json.dumps(books,ensure_ascii=False)+';function bookCard',s,count=1,flags=re.S)
s=re.sub(r'const resources=\[.*?\];let activeFilter', 'const resources='+json.dumps(resources,ensure_ascii=False)+';let activeFilter',s,count=1,flags=re.S)
# Replace legacy renderers and filters, retaining existing styles and navigation.
start=s.index('function bookCard(');end=s.index("document.getElementById('year')",start)
s=s[:start]+'''function safe(x){return String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function safeUrl(x){const v=String(x||'').trim();return /^(https:\\/\\/|\\/media\\/)/i.test(v)?safe(v):'';}
function bookCard(b){let pdf=safeUrl(b.pdf),amazon=safeUrl(b.amazon),cover=safeUrl(b.cover);return `<article class="resource"><div class="bookcover ${safe(b.style||'')}">${cover?`<img src="${cover}" alt="${safe(b.title)} cover" style="width:100%;height:100%;object-fit:contain">`:`<span>LOST THEN FOUND</span><strong>A Journey<br>Through the Bible</strong><em>${safe(b.title)}</em>`}</div><div class="content"><div class="tag">Free devotional PDF</div><h3>${safe(b.title)}</h3><p>${safe(b.description)}</p><div class="actions">${pdf?`<a class="btn primary" href="${pdf}" download>↓ Free PDF</a>`:'<span>PDF coming soon</span>'}${amazon?`<a class="textlink" href="${amazon}" target="_blank" rel="noopener noreferrer">Buy Paperback ↗</a>`:''}</div></div></article>`}
function renderBooks(){let markup=books.length?books.map(bookCard).join(''):'<p>Free devotionals are being prepared. Check back soon!</p>';document.getElementById('homeBooks').innerHTML=markup;document.getElementById('bookGrid').innerHTML=markup;}renderBooks();
''' +s[end:]
start=s.index('const categories=');end=s.index('function navigate(',start)
s=s[:start]+'''const categories=['All',...new Set(resources.map(r=>r.category).filter(Boolean))];document.getElementById('filterBar').innerHTML=categories.map(c=>`<button class="filter ${c==='All'?'active':''}" data-filter="${safe(c)}">${safe(c)}</button>`).join('');document.getElementById('filterBar').addEventListener('click',e=>{const b=e.target.closest('[data-filter]');if(b)setFilter(b.dataset.filter)});function setFilter(c){activeFilter=c;document.querySelectorAll('.filter').forEach(b=>b.classList.toggle('active',b.dataset.filter===c));renderResources()}function renderResources(){let q=document.getElementById('resourceSearch').value.toLowerCase();let arr=resources.filter(r=>(activeFilter==='All'||r.category===activeFilter)&&(r.title+' '+r.description+' '+r.category).toLowerCase().includes(q));document.getElementById('resourceGrid').innerHTML=arr.length?arr.map(r=>`<article class="tile"><div class="tag">${safe(r.category||'Ministry resource')}</div><h3>${safe(r.title)}</h3><p>${safe(r.description)}</p>${safeUrl(r.download)?`<a class="textlink" href="${safeUrl(r.download)}" download>↓ Download resource</a>`:'<span>Download coming soon</span>'}</article>`).join(''):'<p>No resources match your search yet.</p>'}renderResources();
''' +s[end:]
# Journal articles rendered as separate static pages for accessibility and indexing.
for p in posts:
 body=mistune.html(p.get('body',''))
 featured=media_url(p.get('cover') or p.get('image'))
 featured_html=(f'<img src="{html.escape(featured,quote=True)}" alt="{html.escape(str(p.get("title","Journal image")),quote=True)}" style="display:block;width:100%;max-height:480px;object-fit:contain;border-radius:14px;margin:1.5rem 0">' if featured else '')
 page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(str(p.get('title','Journal')))} | Lost Then Found</title><style>body{{margin:0;background:#f8f6f0;color:#243b49;font:18px/1.75 system-ui,sans-serif}}main{{max-width:760px;margin:5rem auto;padding:0 24px}}a{{color:#246c61}}h1{{line-height:1.2}}img{{max-width:100%}}</style></head><body><main><a href="/index.html#journal">← Back to The Journal</a><h1>{html.escape(str(p.get('title','')))}</h1><p>{html.escape(str(p.get('date','')))}</p>{featured_html}{body}</main></body></html>'''
 dest=out/'journal'/p['slug'];dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(page)
if posts:
 cards=''.join(f'''<article class="post"><div class="journal-art">{(f'<img src="{html.escape(media_url(p.get("cover") or p.get("image")),quote=True)}" alt="{html.escape(str(p.get("title","Journal image")),quote=True)}" style="width:100%;height:200px;object-fit:contain">' if media_url(p.get('cover') or p.get('image')) else html.escape(str(p.get('title',''))))}</div><div class="content"><div class="tag">The Journal</div><h3>{html.escape(str(p.get('title','')))}</h3><p>{html.escape(str(p.get('excerpt','')))}</p><a class="textlink" href="/journal/{p['slug']}/">Read article →</a></div></article>''' for p in posts)
 s=re.sub(r'(<section class="page" id="journal".*?<div class="section"><div class="wrap"><div class="grid3">).*?(</div>\s*</div>\s*</div>\s*</section>)',lambda m:m.group(1)+cards+m.group(2),s,count=1,flags=re.S)
else:
 s=re.sub(r'(<section class="page" id="journal".*?<div class="section"><div class="wrap"><div class="grid3">).*?(</div>\s*</div>\s*</div>\s*</section>)',lambda m:m.group(1)+'<p>Journal entries are coming soon.</p>'+m.group(2),s,count=1,flags=re.S)
s=s.replace('Prototype preview · All book covers and resource entries shown here are illustrative placeholders.','Free biblical resources for the journey.')
s=s.replace('Lost Then Found | Adventure in the Word',html.escape(settings.get('title','Lost Then Found'))+' | Adventure in the Word')
(out/'index.html').write_text(s)
if (root/'media').exists():shutil.copytree(root/'media',out/'media',dirs_exist_ok=True)
print(f'Built {len(books)} devotionals, {len(resources)} resources, {len(posts)} published journal posts')
