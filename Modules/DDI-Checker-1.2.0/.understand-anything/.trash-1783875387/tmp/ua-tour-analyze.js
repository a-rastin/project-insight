const fs = require('fs');
const path = require('path');

try {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];
  const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  const layersPath = path.join(path.dirname(inputPath), 'layers.json');
  const rawLayers = fs.existsSync(layersPath) ? JSON.parse(fs.readFileSync(layersPath, 'utf8')) : [];
  const layers = Array.isArray(rawLayers) ? rawLayers : (rawLayers.layers || []);
  const nodes = input.nodes || [];
  const edges = input.edges || [];
  const byId = new Map(nodes.map(n => [n.id, n]));
  const fanIn = new Map(nodes.map(n => [n.id, 0]));
  const fanOut = new Map(nodes.map(n => [n.id, 0]));
  for (const e of edges) {
    fanIn.set(e.target, (fanIn.get(e.target) || 0) + 1);
    fanOut.set(e.source, (fanOut.get(e.source) || 0) + 1);
  }
  const rank = (map, key) => [...map].map(([id, value]) => ({id, [key]: value, name: byId.get(id)?.name || id})).sort((a,b) => b[key]-a[key] || a.id.localeCompare(b.id)).slice(0,20);
  const fanInRanking = rank(fanIn, 'fanIn');
  const fanOutRanking = rank(fanOut, 'fanOut');
  const outValues = [...fanOut.values()].sort((a,b)=>b-a);
  const highOut = outValues[Math.max(0, Math.ceil(outValues.length * 0.1)-1)] || 0;
  const inValues = [...fanIn.values()].sort((a,b)=>a-b);
  const lowIn = inValues[Math.max(0, Math.ceil(inValues.length * 0.25)-1)] || 0;
  const entryNames = new Set(['index.ts','index.js','main.ts','main.js','app.ts','app.js','server.ts','server.js','mod.rs','main.go','main.py','main.rs','manage.py','app.py','wsgi.py','asgi.py','run.py','__main__.py','Application.java','Main.java','Program.cs','config.ru','index.php','App.swift','Application.kt','main.cpp','main.c']);
  const candidates = nodes.map(n => {
    let score = 0;
    const fp = n.filePath || '';
    if (n.type === 'file' && entryNames.has(n.name)) score += 3;
    if (n.type === 'file' && fp.split(/[\\/]/).length <= 2) score += 1;
    if (n.type === 'file' && (fanOut.get(n.id)||0) >= highOut) score += 1;
    if (n.type === 'file' && (fanIn.get(n.id)||0) <= lowIn) score += 1;
    if (n.type === 'document' && fp === 'README.md') score += 5;
    else if (n.type === 'document' && fp.split(/[\\/]/).length === 1 && fp.endsWith('.md')) score += 2;
    return {id:n.id, score, name:n.name, summary:n.summary, type:n.type};
  }).filter(x => x.score > 0).sort((a,b)=>b.score-a.score || a.id.localeCompare(b.id)).slice(0,5);
  const start = candidates.find(c => c.type === 'file')?.id || nodes.find(n => n.type === 'file')?.id;
  const depthMap = {};
  const order = [];
  if (start) {
    const queue = [start]; depthMap[start] = 0;
    while (queue.length) {
      const id = queue.shift(); order.push(id);
      for (const e of edges.filter(e => e.source === id && (e.type === 'imports' || e.type === 'calls'))) {
        if (depthMap[e.target] === undefined) { depthMap[e.target] = depthMap[id] + 1; queue.push(e.target); }
      }
    }
  }
  const byDepth = {};
  for (const id of order) (byDepth[depthMap[id]] ||= []).push(id);
  const projectNode = n => ({id:n.id,name:n.name,type:n.type,summary:n.summary});
  const nonCodeFiles = {
    documentation: nodes.filter(n=>n.type==='document').map(projectNode),
    infrastructure: nodes.filter(n=>['service','pipeline','resource'].includes(n.type)).map(projectNode),
    data: nodes.filter(n=>['table','schema','endpoint'].includes(n.type)).map(projectNode),
    config: nodes.filter(n=>n.type==='config').map(projectNode)
  };
  const mutual = [];
  for (let i=0;i<nodes.length;i++) for (let j=i+1;j<nodes.length;j++) {
    const a=nodes[i].id,b=nodes[j].id;
    const ab=edges.filter(e=>e.source===a&&e.target===b&&['imports','calls'].includes(e.type)).length;
    const ba=edges.filter(e=>e.source===b&&e.target===a&&['imports','calls'].includes(e.type)).length;
    if (ab&&ba) mutual.push({nodes:[a,b],edgeCount:ab+ba});
  }
  const nodeSummaryIndex = Object.fromEntries(nodes.map(n=>[n.id,{name:n.name,type:n.type,summary:n.summary}]));
  fs.writeFileSync(outputPath, JSON.stringify({scriptCompleted:true,entryPointCandidates:candidates,fanInRanking,fanOutRanking,bfsTraversal:{startNode:start,order,depthMap,byDepth},nonCodeFiles,clusters:mutual.slice(0,10),layers:{count:layers.length,list:layers.map(l=>({id:l.id,name:l.name,description:l.description}))},nodeSummaryIndex,totalNodes:nodes.length,totalEdges:edges.length},null,2));
} catch (error) {
  process.stderr.write(error.stack + '\n');
  process.exit(1);
}
