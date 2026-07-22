const fs = require('fs');
const path = require('path');

const root = process.argv[2];
const inter = path.join(root, '.understand-anything', 'intermediate');
const graph = JSON.parse(fs.readFileSync(path.join(inter, 'assembled-graph.json'), 'utf8'));
const scan = JSON.parse(fs.readFileSync(path.join(inter, 'scan-result.json'), 'utf8'));
let layers = JSON.parse(fs.readFileSync(path.join(inter, 'layers.json'), 'utf8'));
let tour = JSON.parse(fs.readFileSync(path.join(inter, 'tour.json'), 'utf8'));
if (!Array.isArray(layers)) layers = layers.layers || [];
if (!Array.isArray(tour)) tour = tour.steps || [];

const nodeIds = new Set(graph.nodes.map(n => n.id));
const prefixes = ['file:', 'config:', 'document:', 'service:', 'pipeline:', 'table:', 'schema:', 'resource:', 'endpoint:'];
const normalizeRef = id => prefixes.some(p => String(id).startsWith(p)) ? String(id) : `file:${id}`;
const slug = s => String(s || 'unnamed').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
layers = layers.map((l, i) => ({
  id: l.id || `layer:${slug(l.name || `layer-${i + 1}`)}`,
  name: l.name || `Layer ${i + 1}`,
  description: l.description || 'No description available',
  nodeIds: (l.nodeIds || l.nodes || []).map(x => normalizeRef(typeof x === 'object' ? x.id : x)).filter(id => nodeIds.has(id))
})).filter(l => l.nodeIds.length);
tour = tour.map((s, i) => ({
  order: Number.isInteger(s.order) ? s.order : i + 1,
  title: s.title || `Step ${i + 1}`,
  description: s.description || s.whyItMatters || 'No description available',
  nodeIds: (s.nodeIds || s.nodesToInspect || []).map(normalizeRef).filter(id => nodeIds.has(id)),
  ...(typeof s.languageLesson === 'string' ? {languageLesson: s.languageLesson} : {})
})).filter(s => s.nodeIds.length).sort((a,b) => a.order - b.order).map((s,i) => ({...s, order:i+1}));

const commit = process.argv[3];
const finalGraph = {
  version: '1.0.0',
  project: {name: scan.name, languages: scan.languages, frameworks: scan.frameworks, description: scan.description, analyzedAt: new Date().toISOString(), gitCommitHash: commit},
  nodes: graph.nodes,
  edges: graph.edges,
  layers,
  tour
};
const issues = [], warnings = [];
const seen = new Set();
for (const [i,n] of finalGraph.nodes.entries()) {
  if (!n.id) issues.push(`Node[${i}] missing id`);
  if (!n.type) issues.push(`Node[${i}] missing type`);
  if (!n.name) issues.push(`Node[${i}] missing name`);
  if (!n.summary) { n.summary = 'No summary available'; warnings.push(`Filled summary for ${n.id}`); }
  if (!Array.isArray(n.tags) || !n.tags.length) { n.tags = ['untagged']; warnings.push(`Filled tags for ${n.id}`); }
  if (seen.has(n.id)) issues.push(`Duplicate node ${n.id}`); seen.add(n.id);
}
finalGraph.edges = finalGraph.edges.filter(e => {
  const ok = nodeIds.has(e.source) && nodeIds.has(e.target);
  if (!ok) warnings.push(`Dropped dangling edge ${e.source} -> ${e.target}`);
  return ok;
});
const assigned = new Map();
const fileTypes = new Set(['file','config','document','service','pipeline','table','schema','resource','endpoint']);
for (const l of layers) for (const id of l.nodeIds) {
  if (assigned.has(id)) issues.push(`Node ${id} assigned to multiple layers`);
  assigned.set(id,l.id);
}
for (const n of finalGraph.nodes.filter(n => fileTypes.has(n.type))) if (!assigned.has(n.id)) issues.push(`File node ${n.id} not assigned to a layer`);
for (const s of tour) for (const id of s.nodeIds) if (!nodeIds.has(id)) issues.push(`Tour ref missing ${id}`);
const stats = {totalNodes:finalGraph.nodes.length,totalEdges:finalGraph.edges.length,totalLayers:layers.length,tourSteps:tour.length,nodeTypes:{},edgeTypes:{}};
for (const n of finalGraph.nodes) stats.nodeTypes[n.type]=(stats.nodeTypes[n.type]||0)+1;
for (const e of finalGraph.edges) stats.edgeTypes[e.type]=(stats.edgeTypes[e.type]||0)+1;
fs.writeFileSync(path.join(inter, 'assembled-graph.json'), JSON.stringify(finalGraph,null,2));
fs.writeFileSync(path.join(inter, 'review.json'), JSON.stringify({issues,warnings,stats},null,2));
if (issues.length) process.exitCode = 2;
