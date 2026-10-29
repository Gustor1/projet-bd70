const fs=require('fs'),path=require('path');
const {instance}=require(process.env.BD70_VIZ||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@viz-js/viz');
(async()=>{const v=await instance();for(const f of fs.readdirSync(__dirname).filter(x=>x.endsWith('.dot'))){const s=fs.readFileSync(path.join(__dirname,f),'utf8');for(const fmt of ['svg','json'])fs.writeFileSync(path.join(__dirname,f.replace(/\.dot$/,'.'+fmt)),v.renderString(s,{format:fmt,engine:'dot'}));}})().catch(e=>{console.error(e);process.exit(1)});
