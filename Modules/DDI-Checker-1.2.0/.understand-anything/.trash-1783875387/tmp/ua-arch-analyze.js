const fs = require('fs');

try {
  const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const nodes = input.fileNodes || [];
  const imports = input.importEdges || [];
  const allEdges = input.allEdges || [];
  const byId = new Map(nodes.map(n => [n.id, n]));
  const paths = nodes.map(n => (n.filePath || '').replace(/\\/g, '/'));
  const split = paths.map(p => p.split('/'));
  let common = [];
  if (split.length) {
    for (let i = 0; i < Math.min(...split.map(x => x.length - 1)); i++) {
      if (split.every(x => x[i] === split[0][i])) common.push(split[0][i]); else break;
    }
  }
  function groupFor(n) {
    const p = (n.filePath || '').replace(/\\/g, '/');
    const parts = p.split('/').slice(common.length);
    if (parts.length > 1) return parts[0];
    const name = parts[0] || p;
    if (/\.(test|spec)\./i.test(name) || /^test_/i.test(name)) return 'test';
    if (/config|package\.json|Cargo\.toml|go\.mod|Gemfile|pom\.xml|build\.gradle|composer\.json/i.test(name)) return 'config';
    return 'root';
  }
  const directoryGroups = {}, nodeTypeGroups = {}, groupById = {};
  for (const n of nodes) {
    const g = groupFor(n); groupById[n.id] = g;
    (directoryGroups[g] ||= []).push(n.id);
    (nodeTypeGroups[n.type] ||= []).push(n.id);
  }
  const fanIn = Object.fromEntries(nodes.map(n => [n.id, 0]));
  const fanOut = Object.fromEntries(nodes.map(n => [n.id, 0]));
  const inter = new Map();
  for (const e of imports) {
    if (!byId.has(e.source) || !byId.has(e.target)) continue;
    fanOut[e.source]++; fanIn[e.target]++;
    const a = groupById[e.source], b = groupById[e.target];
    if (a !== b) inter.set(`${a}\0${b}`, (inter.get(`${a}\0${b}`) || 0) + 1);
  }
  const interGroupImports = [...inter].map(([k, count]) => { const [from, to] = k.split('\0'); return {from, to, count}; });
  const density = {};
  for (const g of Object.keys(directoryGroups)) {
    let internalEdges = 0, totalEdges = 0;
    for (const e of imports) {
      const a = groupById[e.source], b = groupById[e.target];
      if (a === g || b === g) totalEdges++;
      if (a === g && b === g) internalEdges++;
    }
    density[g] = {internalEdges, totalEdges, density: totalEdges ? internalEdges / totalEdges : 0};
  }
  const patterns = {routes:'api',api:'api',controllers:'api',endpoints:'api',handlers:'api',services:'service',core:'service',lib:'service',domain:'service',logic:'service',models:'data',db:'data',data:'data',persistence:'data',repository:'data',entities:'data',components:'ui',views:'ui',pages:'ui',ui:'ui',layouts:'ui',screens:'ui',utils:'utility',helpers:'utility',common:'utility',shared:'utility',tools:'utility',config:'config',test:'test',tests:'test',spec:'test',specs:'test',src:'service',scripts:'utility',docs:'documentation'};
  const patternMatches = {};
  for (const g of Object.keys(directoryGroups)) if (patterns[g.toLowerCase()]) patternMatches[g] = patterns[g.toLowerCase()];
  const cross = new Map();
  for (const e of allEdges) {
    const a = byId.get(e.source), b = byId.get(e.target); if (!a || !b) continue;
    const k = `${a.type}\0${b.type}\0${e.type}`; cross.set(k, (cross.get(k) || 0) + 1);
  }
  const crossCategoryEdges = [...cross].map(([k,count]) => {const [fromType,toType,edgeType]=k.split('\0'); return {fromType,toType,edgeType,count};});
  const dependencyDirection = [];
  const pairs = new Set(interGroupImports.map(x => [x.from,x.to].sort().join('\0')));
  for (const p of pairs) { const [a,b]=p.split('\0'); const ab=inter.get(`${a}\0${b}`)||0, ba=inter.get(`${b}\0${a}`)||0; if(ab>ba) dependencyDirection.push({dependent:a,dependsOn:b}); else if(ba>ab) dependencyDirection.push({dependent:b,dependsOn:a}); }
  const infraFiles = paths.filter(p => /(^|\/)(Dockerfile|docker-compose|compose\.(ya?ml)|Jenkinsfile|\.gitlab-ci\.yml)|\.tf(vars)?$|^\.github\/workflows\//i.test(p));
  const dataPipeline = {schemaFiles: paths.filter(p => /\.(sql|graphql|gql|proto|prisma)$/i.test(p)), migrationFiles: paths.filter(p => /(^|\/)migrations?\//i.test(p)), dataModelFiles: paths.filter(p => /(^|\/)(models?|data|entities)\//i.test(p)), apiHandlerFiles: paths.filter(p => /(^|\/)(routes?|controllers?|handlers?|api)\//i.test(p))};
  const groups = Object.keys(directoryGroups); const withDocs = groups.filter(g => directoryGroups[g].some(id => /\.(md|rst)$/i.test(byId.get(id).filePath || '')));
  const result = {
    scriptCompleted:true, directoryGroups, nodeTypeGroups, crossCategoryEdges, interGroupImports,
    intraGroupDensity:density, patternMatches,
    deploymentTopology:{hasDockerfile:infraFiles.some(p=>/(^|\/)Dockerfile/i.test(p)),hasCompose:infraFiles.some(p=>/(docker-compose|compose\.ya?ml)/i.test(p)),hasK8s:paths.some(p=>/(^|\/)(k8s|kubernetes|helm|charts)\//i.test(p)),hasTerraform:paths.some(p=>/\.tf(vars)?$/i.test(p)),hasCI:paths.some(p=>/^\.github\/workflows\/|^\.gitlab-ci\.yml$|Jenkinsfile/i.test(p)),infraFiles},
    dataPipeline,
    docCoverage:{groupsWithDocs:withDocs.length,totalGroups:groups.length,coverageRatio:groups.length?withDocs.length/groups.length:0,undocumentedGroups:groups.filter(g=>!withDocs.includes(g))},
    dependencyDirection,
    fileStats:{totalFileNodes:nodes.length,filesPerGroup:Object.fromEntries(groups.map(g=>[g,directoryGroups[g].length])),nodeTypeCounts:Object.fromEntries(Object.entries(nodeTypeGroups).map(([k,v])=>[k,v.length]))},
    fileFanIn:fanIn,fileFanOut:fanOut
  };
  fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2));
} catch (e) { console.error(e.stack || e.message); process.exit(1); }
