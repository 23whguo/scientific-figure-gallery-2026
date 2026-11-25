"""Real browser checks against the static site, including GitHub project paths."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8790/');args=parser.parse_args()
    out=ROOT/'test-artifacts';out.mkdir(exist_ok=True)
    checks=[];errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
        context=browser.new_context(viewport={'width':1480,'height':1050},accept_downloads=True)
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(args.url,wait_until='networkidle')
        assert page.locator('.figure-card').count()==100
        assert page.locator('.figure-card img').first.evaluate('(i)=>i.complete&&i.naturalWidth>0')
        checks.append('2,831 figure catalog and lazy thumbnail grid loads')
        page.locator('#venueChips [data-value=emnlp]').click()
        assert '171' in page.locator('#resultCount').inner_text()
        page.locator('#next').click();assert page.locator('.figure-card').count()==71
        page.locator('#page').fill('1');page.locator('#go').click();assert page.locator('.figure-card').count()==100
        checks.append('venue filtering, pagination and page jump')
        page.locator('#reset').click();page.locator('#search').fill('OctoTools')
        page.wait_for_function("document.querySelectorAll('.figure-card').length>0&&document.querySelector('.figure-title').textContent.includes('OctoTools')")
        assert all('OctoTools' in s for s in page.locator('.figure-title').all_inner_texts())
        checks.append('full-text search')
        card=page.locator('.figure-card').first;figure_id=card.get_attribute('data-id')
        card.locator('.card-save').click();page.reload(wait_until='networkidle')
        assert page.locator('.card-save').first.get_attribute('aria-pressed')=='true'
        page.locator('.figure-image').first.click()
        assert page.locator('#detail').is_visible()
        page.wait_for_function("document.querySelector('#detailImage').complete&&document.querySelector('#detailImage').naturalWidth>0")
        assert page.locator('#detailCaption').inner_text()
        assert page.locator('#paperLink').get_attribute('href').startswith('https://')
        page.locator('#zoomIn').click();assert page.locator('#zoomReset').inner_text()=='125%'
        page.locator('#zoomReset').click();assert page.locator('#zoomReset').inner_text()=='100%'
        shared=page.url
        page.reload(wait_until='networkidle');assert page.locator('#detail').is_visible()
        checks.append('persistent favorite, full-size image, zoom and reloadable figure link')
        page.locator('#editPrimary').select_option('concept')
        page.locator('#editSecondary input[value=flow]').check()
        page.locator('#saveCategory').click()
        page.locator('#note').fill('布局参考：模块关系清晰')
        page.locator('#detailClose').click();page.reload(wait_until='networkidle')
        page.locator('.figure-image').first.click()
        assert page.locator('#editPrimary').input_value()=='concept'
        assert page.locator('#editSecondary input[value=flow]').is_checked()
        assert page.locator('#note').input_value()=='布局参考：模块关系清晰'
        page.locator('#detailClose').click()
        checks.append('primary/secondary corrections and notes persist')
        with page.expect_download() as downloaded:page.locator('#backup').click()
        backup=Path(downloaded.value.path());record=json.loads(backup.read_text(encoding='utf-8'))
        assert figure_id in record['favorites'] and record['categories'][figure_id]['primary']=='concept'
        page.evaluate('localStorage.clear()');page.reload(wait_until='networkidle')
        page.locator('#importFile').set_input_files(str(backup))
        page.wait_for_function("document.querySelector('#favoriteCount').textContent==='1'")
        with page.expect_download() as exported:page.locator('#export').click()
        export=json.loads(Path(exported.value.path()).read_text(encoding='utf-8'))
        assert export['figures'] and export['figures'][0]['caption']
        assert export['figures'][0]['classification']['primary']=='concept'
        checks.append('collection backup/import and results JSON preserves paper/caption/category')
        page.locator('#favoriteSide').click();assert page.locator('.figure-card').count()==1
        page.locator('#allNav').click();page.locator('#reset').click()
        page.locator('#typeChips [data-value=flow]').click()
        page.locator('#match').select_option('primary')
        assert all(x=='流程图' for x in page.locator('.card-category').all_inner_texts())
        page.locator('#match').select_option('secondary')
        assert page.locator('.figure-card').count()>0
        page.locator('#tier').select_option('best')
        if page.locator('.figure-card').count():assert all('Best' in x for x in page.locator('.ribbon').all_inner_texts())
        page.locator('#reset').click();page.locator('#sort').select_option('title')
        titles=page.locator('.figure-title').all_inner_texts();assert len(titles)==100
        page.locator('#random').click();assert page.locator('#detail').is_visible();page.locator('#detailClose').click()
        checks.append('primary/secondary-only, acceptance filters, title sort and random browse')
        page.locator('#language').click();assert page.locator('html').get_attribute('lang')=='en'
        assert page.locator('#sectionTitle').inner_text()=='Find your next visual inspiration'
        page.locator('#theme').click();assert page.locator('html').get_attribute('data-theme')=='dark'
        page.locator('#theme').click();page.locator('#language').click();page.locator('#reset').click()
        page.screenshot(path=str(out/'desktop.png'))
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(out/'mobile.png'))
        checks.append('English, dark/light themes and mobile layout')
        page.set_viewport_size({'width':1480,'height':1050});page.locator('#search').fill('no_such_figure_xyz_3819274')
        page.wait_for_selector('#empty',state='visible');page.locator('#emptyReset').click()
        assert page.locator('.figure-card').count()==100
        page.keyboard.press('/');assert page.locator('#search').evaluate('(e)=>e===document.activeElement')
        page.locator('#search').blur();page.locator('.figure-image').first.click();page.keyboard.press('Escape')
        assert not page.locator('#detail').is_visible()
        checks.append('empty state reset and keyboard search/dialog handling')
        page.goto(shared,wait_until='networkidle');assert page.locator('#detail').is_visible()
        page.locator('#detailClose').click()
        page.goto(args.url+'docs/about.html',wait_until='networkidle');assert page.locator('h1').is_visible()
        page.goto(args.url+'docs/methodology.html',wait_until='networkidle');assert page.locator('h1').is_visible()
        checks.append('shared deep link and source/methodology documents')
        assert not errors,errors
        browser.close()
    report={'passed':True,'url':args.url,'checks':checks,'page_errors':errors}
    (out/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))


if __name__=='__main__':main()
