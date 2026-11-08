// Copie PDF vectorielle du diaporama : node scripts/export-diapo-pdf.cjs livrables/soutenance/Transit-diapo.html docs/soutenance/Transit.pdf
const {chromium}=require('C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const [file,out]=process.argv.slice(2);
(async()=>{const b=await chromium.launch({headless:true,channel:'msedge'});const p=await b.newPage({viewport:{width:1920,height:1080},reducedMotion:'reduce'});
await p.goto(require('url').pathToFileURL(file).href);await p.waitForTimeout(800);
await p.pdf({path:out,width:'1440px',height:'810px',printBackground:true,preferCSSPageSize:true});await b.close();})().catch(e=>{console.error(e);process.exit(1)});
