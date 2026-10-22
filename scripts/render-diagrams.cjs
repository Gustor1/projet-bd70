const fs=require('fs');const path=require('path');
const {instance}=require(process.env.BD70_VIZ||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@viz-js/viz');
(async()=>{const viz=await instance();for(const file of fs.readdirSync('docs/diagrammes').filter(f=>f.endsWith('.dot'))){const src=fs.readFileSync(path.join('docs/diagrammes',file),'utf8');fs.writeFileSync(path.join('docs/diagrammes',file.replace('.dot','.svg')),viz.renderString(src,{format:'svg',engine:'dot'}));console.log(file);} })().catch(e=>{console.error(e);process.exit(1)});
