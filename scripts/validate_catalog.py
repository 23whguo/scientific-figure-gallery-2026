"""Validate portable public assets, identity, metadata and publication exclusions."""
import json
from collections import Counter
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def main():
    figures=json.loads((ROOT/'data/figures.json').read_text(encoding='utf-8'))
    catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    assert len(figures)==2831==catalog['count']
    assert len({f['id'] for f in figures})==len(figures)
    assert Counter(f['venue'] for f in figures)=={'iclr':1017,'cvpr':660,'acl':983,'emnlp':171}
    assert len({f['venue']+':'+f['paper_id'] for f in figures})==catalog['papers']
    size=0
    for f in figures:
        assert f['year']==2026 and f['title'] and f['authors'] and f['paper'].startswith('https://'),f['id']
        assert f['primary'] in catalog['types']
        assert all(k in catalog['types'] and k!=f['primary'] for k in f['secondary'])
        assert re.fullmatch('[a-f0-9]{64}',f['preview_sha256'])
        for key in ('image','thumbnail'):
            path=(ROOT/f[key]).resolve()
            assert path.is_relative_to(ROOT) and path.is_file(),f[key]
            assert path.suffix=='.webp' and path.read_bytes()[:4]==b'RIFF',f[key]
            size+=path.stat().st_size
    def check_public(value):
        if isinstance(value,str):
            assert not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]|\bsk-[a-zA-Z0-9]{15,}',value)
        elif isinstance(value,dict):
            assert not {'source_path','pptx_path','api_key'}.intersection(value)
            for child in value.values():check_public(child)
        elif isinstance(value,list):
            for child in value:check_public(child)
    check_public(figures)
    js=(ROOT/'assets/figures.js').read_text(encoding='utf-8')
    assert json.loads(js.split('window.FIGURES=',1)[1].split(';\nwindow.CATALOG=',1)[0])==figures
    assert not list(ROOT.rglob('*.pptx')) and not list(ROOT.rglob('*.ppt'))
    assert size<1024**3,'Pages artifact must stay below 1 GB'
    for doc in ('index.html','docs/about.html','docs/methodology.html','assets/app.js','assets/style.css'):
        assert (ROOT/doc).is_file()
    print(json.dumps({'passed':True,'figures':len(figures),'papers':catalog['papers'],
        'venues':catalog['venues'],'image_mb':round(size/1048576,1),'ppt_files':0,'local_paths_or_keys':0}))


if __name__=='__main__':main()
