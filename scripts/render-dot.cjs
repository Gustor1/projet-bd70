// Rend des fichiers DOT en SVG vectoriel avec viz.js : node scripts/render-dot.cjs a.dot b.dot
const fs=require('fs');
const {instance}=require(process.env.BD70_VIZ||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@viz-js/viz');
(async()=>{const viz=await instance();for(const file of process.argv.slice(2)){fs.writeFileSync(file.replace(/\.dot$/,'.svg'),viz.renderString(fs.readFileSync(file,'utf8'),{format:'svg',engine:'dot'}));console.log(file.replace(/\.dot$/,'.svg'));}})().catch(e=>{console.error(e);process.exit(1)});
