import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer';
import pa11y from 'pa11y';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const aChecker = require('accessibility-checker');
const lighthouse = (await import('lighthouse')).default;
const chromeLauncher = await import('chrome-launcher');

const PAGES = JSON.parse(fs.readFileSync('pages.json','utf8'));
const OUT = 'raw'; fs.mkdirSync(OUT, {recursive:true});
const AXE_PATH = require.resolve('axe-core/axe.min.js');
const CHROME = puppeteer.executablePath();
const VIEW = {width:1366, height:900};
const only = process.argv[2] ? process.argv[2].split(',') : null;
const log = (m) => { const l = `[${new Date().toISOString()}] ${m}`; console.log(l); fs.appendFileSync('collect.log', l+'\n'); };
const save = (name, obj) => fs.writeFileSync(path.join(OUT, name), JSON.stringify(obj, null, 1));

async function withPage(fn) {
  const browser = await puppeteer.launch({executablePath: CHROME, headless: true, args:['--no-sandbox','--disable-gpu']});
  try { const page = await browser.newPage(); await page.setViewport(VIEW); return await fn(page); }
  finally { await browser.close(); }
}
async function goto(page, url) {
  await page.goto(url, {waitUntil:'networkidle2', timeout: 120000});
  await new Promise(r => setTimeout(r, 2500));
}

async function runAxe(id, url) {
  return withPage(async (page) => {
    await goto(page, url);
    await page.addScriptTag({path: AXE_PATH});
    const res = await page.evaluate(async () => await axe.run(document, {runOnly:{type:'tag', values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}, resultTypes:['violations','incomplete','passes','inapplicable']}));
    const rules = await page.evaluate(() => axe.getRules());
    save(`${id}.axe.json`, {id, url, engine:'axe-core', version: res.testEngine.version, ua: res.testEnvironment.userAgent, timestamp: res.timestamp, violations: res.violations, incomplete: res.incomplete, passes: res.passes.map(p=>({id:p.id,tags:p.tags,nodes:p.nodes.length})), inapplicable: res.inapplicable.map(p=>p.id), rules});
    return res.violations.length;
  });
}

async function runIbm(id, url) {
  return withPage(async (page) => {
    await goto(page, url);
    const r = await aChecker.getCompliance(page, id);
    const report = r.report;
    save(`${id}.ibm.json`, {id, url, engine:'ibm-equal-access', version: JSON.parse(fs.readFileSync('node_modules/accessibility-checker/package.json','utf8')).version, ruleArchive: report?.summary?.ruleArchive, policies: report?.summary?.policies, counts: report?.summary?.counts, results: report?.results, nls: report?.nls});
    return report?.summary?.counts;
  });
}

async function runHtmlcs(id, url) {
  const r = await pa11y(url, {standard:'WCAG2AA', runners:['htmlcs'], includeWarnings:true, includeNotices:true, timeout: 180000, wait: 2500, viewport: VIEW, chromeLaunchConfig:{executablePath: CHROME, args:['--no-sandbox','--disable-gpu']}});
  save(`${id}.htmlcs.json`, {id, url, engine:'html_codesniffer', version: require('html_codesniffer/package.json').version, pa11y: require('pa11y/package.json').version, documentTitle: r.documentTitle, issues: r.issues});
  return r.issues.filter(i=>i.type==='error').length;
}

async function runLighthouse(id, url) {
  const chrome = await chromeLauncher.launch({chromePath: CHROME, chromeFlags:['--headless=new','--no-sandbox','--disable-gpu']});
  try {
    const r = await lighthouse(url, {port: chrome.port, onlyCategories:['accessibility'], output:'json', logLevel:'error', formFactor:'desktop', screenEmulation:{mobile:false, width:1366, height:900, deviceScaleFactor:1, disabled:false}, throttlingMethod:'provided', maxWaitForLoad: 120000});
    const lhr = r.lhr;
    const audits = Object.fromEntries(Object.entries(lhr.audits).map(([k,a]) => [k, {id:a.id, title:a.title, score:a.score, scoreDisplayMode:a.scoreDisplayMode, items:(a.details&&a.details.items)?a.details.items.length:null}]));
    save(`${id}.lighthouse.json`, {id, url, engine:'lighthouse', version: lhr.lighthouseVersion, ua: lhr.environment.hostUserAgent, fetchTime: lhr.fetchTime, score: lhr.categories.accessibility.score, auditRefs: lhr.categories.accessibility.auditRefs, audits});
    return lhr.categories.accessibility.score;
  } finally { await chrome.kill(); }
}

const TOOLS = {axe: runAxe, ibm: runIbm, htmlcs: runHtmlcs, lighthouse: runLighthouse};
const toolsToRun = process.argv[3] ? process.argv[3].split(',') : Object.keys(TOOLS);
for (const [id, p] of Object.entries(PAGES)) {
  if (only && !only.includes(id)) continue;
  for (const t of toolsToRun) {
    const f = path.join(OUT, `${id}.${t}.json`);
    if (fs.existsSync(f)) { log(`${id} ${t}: cached`); continue; }
    try { const s = await TOOLS[t](id, p.url); log(`${id} ${t}: ok ${JSON.stringify(s)}`); }
    catch (e) { log(`${id} ${t}: ERROR ${e.message.split('\n')[0]}`); save(`${id}.${t}.error.json`, {id, url:p.url, error: String(e.stack||e)}); }
  }
}
log('done');
