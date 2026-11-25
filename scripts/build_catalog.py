"""Build a portable public gallery from local selections, without PPT or secrets."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CONFERENCES = Path(r'D:\allama\ACL_EMNLP_CVPR_figure_categories')
ICLR = Path(r'D:\allama\HF_ICLR_figure_categories\clef_classification')
EXPORTS = Path(r'D:\allama\PPT_exports_20261122_TeX')
LABELS = {'overview':'框架总览','flow':'流程图','architecture':'架构图','benchmark':'Benchmark 图',
 'survey':'综述图','concept':'概念图','contrast':'比较图','comparison':'结果对比',
 'statistics':'数据统计','visualization':'数据展示图','other':'其他','uncertain':'待确认'}
EN = {'overview':'Framework overview','flow':'Workflow','architecture':'Architecture','benchmark':'Benchmark',
 'survey':'Survey','concept':'Concept','contrast':'Method comparison','comparison':'Results comparison',
 'statistics':'Data statistics','visualization':'Data visualization','other':'Other','uncertain':'Uncertain'}
PATTERNS = {'overview':'framework','flow':'pipeline','architecture':'architecture','benchmark':'taxonomy',
 'survey':'taxonomy','concept':'conceptual','contrast':'comparison','comparison':'results',
 'statistics':'results','visualization':'results','other':'teaser','uncertain':'teaser'}


def js(path):
    text = path.read_text(encoding='utf-8-sig')
    return json.loads(text[text.index('=')+1:].strip().rstrip(';'))


def safe_url(url):
    return url if isinstance(url, str) and re.match(r'^https?://[^\s]+$',url) else ''


def prepare(entry):
    row, base, paper = entry
    venue = row['dataset'].removesuffix('2026')
    image = (base / row['image']).resolve(strict=True)
    if hashlib.sha256(image.read_bytes()).hexdigest() != row['preview_sha256']:
        raise ValueError('Preview identity changed: '+row['key'])
    uid = venue+'2026-'+row['id']
    full = Path('images')/venue/'final'/(uid+'.webp')
    thumb = Path('images')/venue/'thumbs'/(uid+'.webp')
    for path in (full,thumb):(ROOT/path).parent.mkdir(parents=True,exist_ok=True)
    with Image.open(image) as source:
        img=ImageOps.exif_transpose(source).convert('RGB')
        width,height=img.size
        if not (ROOT/full).exists():img.save(ROOT/full,'WEBP',quality=93,method=5)
        if not (ROOT/thumb).exists():
            img.thumbnail((680,680),Image.Resampling.LANCZOS);img.save(ROOT/thumb,'WEBP',quality=82,method=5)
    auto=row.get('public_classification',row['auto']);primary=auto['primary'];secondary=[k for k in auto.get('secondary',[]) if k in LABELS and k!=primary]
    authors=paper.get('authors',[])
    if not isinstance(authors,list):authors=[str(authors)] if authors else []
    acceptance=str(paper.get('acceptance',''))
    tier='oral' if re.search(r'oral|口头',acceptance,re.I) else 'spotlight' if re.search(r'spotlight|焦点',acceptance,re.I) else 'poster' if re.search(r'poster|海报',acceptance,re.I) else ''
    award='best' if re.search(r'best|outstanding|最佳|杰出',acceptance,re.I) else ''
    return {'id':uid,'key':row['key'],'asset_id':row['id'],'paper_id':row['paper_id'],
        'venue':venue,'year':2026,'title':row['title'],'authors':authors,
        'abstract':paper.get('abstract',''),'caption':row.get('caption',''),
        'figure_number':row.get('figure_number'),'primary':primary,'secondary':secondary,
        'pattern':PATTERNS[primary],'image':full.as_posix(),'thumbnail':thumb.as_posix(),
        'w':width,'h':height,'paper':safe_url(row.get('paper_url')) or safe_url(paper.get('paper_url')),
        'pdf_source':safe_url(paper.get('conference_pdf_url')) or safe_url(paper.get('pdf_url')),
        'arxiv':safe_url(paper.get('arxiv_url')),'code':safe_url(paper.get('project_url')) or safe_url(paper.get('code_url')),
        'proceedings':safe_url(paper.get('proceedings_url')),'tier':tier,'award':award,
        'track':paper.get('track',''),'acceptance':acceptance,'topic':paper.get('topic',''),
        'version_id':row['version_id'],'preview_sha256':row['preview_sha256'],
        'classification':{'method':row.get('classification_method','clef_systemone'),'primary':primary,'secondary':secondary},
        'attribution':{'title':row['title'],'authors':authors,'source':safe_url(row.get('paper_url')),
                       'notice':'Figure rights remain with the original authors and publishers.'}}


def main():
    for directory in ('data','assets','docs','tests','scripts','.github/workflows'):(ROOT/directory).mkdir(parents=True,exist_ok=True)
    conference=js(CONFERENCES/'data.js');iclr=js(ICLR/'data.js')
    human_export=Path(r'D:\allama\hf-iclr-ppt-categories-review.json')
    corrections={}
    if human_export.exists():
        for r in json.loads(human_export.read_text(encoding='utf-8-sig')).get('figures',[]):
            c=r.get('classification',{})
            if c.get('source')=='human' or c.get('reviewed'):
                corrections[r['key']]=r
    applied=0
    for r in iclr['rows']:
        saved=corrections.get(r['key'])
        if saved and saved.get('revision')==r['revision']:
            c=saved['classification']
            if c['primary'] in LABELS and all(s in LABELS for s in c.get('secondary',[])):
                r['public_classification']=c;r['classification_method']='human_reviewed';applied+=r['dataset']=='iclr2026'
    print('Applied matching exported human ICLR category records:',applied,flush=True)
    selected=json.loads((EXPORTS/'iclr2026-selection.json').read_text(encoding='utf-8-sig'))
    papers={r['id']:r['paper'] for r in selected['figures']}
    entries=[(r,CONFERENCES,r['paper']) for r in conference['rows']]
    entries += [(r,ICLR,papers[r['id']]) for r in iclr['rows'] if r['dataset']=='iclr2026']
    with ThreadPoolExecutor(max_workers=6) as pool:figures=list(pool.map(prepare,entries))
    assert len(figures)==2831 and len({f['id'] for f in figures})==2831
    figures.sort(key=lambda f:({'iclr':0,'cvpr':1,'acl':2,'emnlp':3}[f['venue']],f['paper_id'],str(f['figure_number'])))
    meta={'schema':1,'title':'科研图鉴 · Figure Atlas','year':2026,'updated_at':datetime.now(timezone.utc).isoformat(),
        'count':len(figures),'papers':len({f['venue']+':'+f['paper_id'] for f in figures}),
        'venues':dict(Counter(f['venue'] for f in figures)),
        'types':{key:{'zh':name,'en':EN[key]} for key,name in LABELS.items()},
        'source':'Manually selected figures; JEV/CLEF primary and secondary classification',
        'reference':'https://github.com/qwdwqfwq/topconf-paper-figure-gallery'}
    (ROOT/'data/figures.json').write_text(json.dumps(figures,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (ROOT/'data/catalog.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    # JS companion allows the same site to open directly via file://.
    (ROOT/'assets/figures.js').write_text('window.FIGURES='+json.dumps(figures,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+';\nwindow.CATALOG='+json.dumps(meta,ensure_ascii=False).replace('<','\\u003c')+';',encoding='utf-8')
    print(json.dumps({'figures':len(figures),'venues':meta['venues'],'papers':meta['papers'],
        'image_mb':round(sum(f.stat().st_size for f in (ROOT/'images').rglob('*.webp'))/1048576,1)},ensure_ascii=True),flush=True)


if __name__=='__main__':main()
