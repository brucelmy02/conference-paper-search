"""Render an offline, searchable reading list from the shared output bundle.

The output has no remote dependencies. Paper data is embedded as inert JSON and
rendered with DOM text nodes; neither user input nor paper text becomes markup.
"""

from __future__ import annotations

import html
import json


def render_html(bundle: dict) -> str:
    """Return a self-contained HTML document for a validated report bundle."""
    metadata = bundle.get("metadata", {})
    title = " ".join(str(metadata.get(key) or "").strip()
                     for key in ("conference", "year")).strip() or "会议论文"
    serialized = json.dumps(bundle, ensure_ascii=False, allow_nan=False)
    # A script element is a raw-text context even with application/json. Escape
    # its terminator, HTML metacharacters, and JS-sensitive Unicode separators.
    serialized = (serialized.replace("&", "\\u0026")
                  .replace("<", "\\u003c").replace(">", "\\u003e")
                  .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    return (_DOCUMENT.replace("__DOCUMENT_TITLE__", html.escape(title, quote=True))
            .replace("__BUNDLE_JSON__", serialized))


_DOCUMENT = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>__DOCUMENT_TITLE__ · 研究阅读清单</title>
<style>
:root{--paper:#f6f5ef;--surface:#fffefa;--ink:#182a31;--muted:#5b6b72;--line:#dce2dc;--accent:#116a68;--light:#e7f1ec;--amber:#8b6318;--radius:15px}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;font-size:14px;line-height:1.65}button,input,select{font:inherit}button,select{cursor:pointer}button,a,input,select,summary{touch-action:manipulation}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #4eaaa4;outline-offset:3px}button{color:inherit}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}h1,h2,h3,p{margin-top:0}h1{font-size:clamp(28px,4vw,42px);line-height:1.25;letter-spacing:-.8px;margin-bottom:12px}h2{font-size:20px;line-height:1.4}h3{font-size:16px;line-height:1.5}p{margin-bottom:12px}.shell{max-width:1240px;margin:auto;padding:32px 34px 60px}.masthead{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-bottom:34px}.brand{display:flex;gap:10px;align-items:center;font-weight:700;letter-spacing:.3px}.brand-symbol{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:var(--ink);color:var(--surface)}.offline{font-size:12px;color:var(--muted);display:flex;gap:7px;align-items:center}.offline:before{content:"";width:7px;height:7px;border-radius:50%;background:var(--accent)}.hero{display:grid;grid-template-columns:1.7fr 1fr;gap:36px;align-items:start;margin-bottom:24px}.eyebrow{color:var(--accent);font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:10px}.lead{font-size:15px;color:var(--muted);max-width:720px}.hero-meta{font-size:12px;color:var(--muted);display:flex;gap:8px 14px;flex-wrap:wrap}.interest{border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;background:var(--surface)}.interest h2{font-size:14px;margin-bottom:12px}.interest-item{margin-bottom:12px}.interest-item:last-child{margin-bottom:0}.interest-item strong{font-size:13px;display:block}.interest-item p{font-size:12px;color:var(--muted);margin:4px 0 0}.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0 10px}.stat{padding:15px 18px;background:var(--surface);border:1px solid var(--line);border-radius:12px}.stat strong{font-size:25px;line-height:1.25;display:block;font-weight:700;font-variant-numeric:tabular-nums}.stat span{color:var(--muted);font-size:12px}.stat.primary{background:var(--ink);color:white;border-color:var(--ink)}.stat.primary span{color:#c6d5d6}.coverage-note{font-size:12px;color:var(--muted);margin:10px 0 28px}.overview{margin:0 0 28px}.overview-heading{display:flex;align-items:center;gap:10px}.section-kicker{font-size:11px;letter-spacing:1px;color:var(--muted)}.theme-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.theme{background:var(--surface);border:1px solid var(--line);padding:17px 19px;border-radius:var(--radius)}.theme h3{font-size:14px;margin-bottom:6px}.theme p{color:var(--muted);font-size:13px}.inline-ids{display:flex;gap:6px;flex-wrap:wrap}.text-button{border:0;background:none;padding:0;color:var(--accent);font-size:12px;text-align:left}.workbench{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:23px 24px;margin-bottom:20px}.workbench-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:16px}.workbench-head h2{margin:0}.segmented{display:flex;gap:3px;background:var(--paper);border:1px solid var(--line);border-radius:9px;padding:3px}.segmented button{border:none;background:none;border-radius:6px;padding:5px 13px;font-size:12px;color:var(--muted)}.segmented button[aria-pressed="true"]{background:var(--ink);color:white}.search-wrap{position:relative}.search-wrap label{position:absolute;left:14px;top:12px;color:var(--muted);font-size:16px;pointer-events:none}.search-wrap input{border:1px solid #bacac6;background:#fff;padding:11px 15px 11px 42px;border-radius:9px;width:100%;color:var(--ink)}.filter-grid{display:grid;grid-template-columns:1.3fr 1fr .9fr 1fr 1fr;gap:12px;margin-top:13px}.filter-grid label{font-size:11px;color:var(--muted);display:block}.filter-grid select{display:block;width:100%;margin-top:4px;border:1px solid var(--line);padding:7px 9px;border-radius:7px;background:var(--surface);color:var(--ink);font-size:12px;min-width:0}.results-bar{display:flex;justify-content:space-between;align-items:center;gap:15px;margin:16px 2px 0;color:var(--muted);font-size:12px}.clear-button{border:none;background:none;color:var(--accent);padding:2px 0}.reading-note{font-size:11px;color:var(--muted);margin:12px 0 0}.cards{display:grid;gap:14px}.paper-card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px 24px;scroll-margin-top:20px}.paper-top{display:flex;justify-content:space-between;gap:20px;align-items:center}.card-index{display:flex;align-items:center;gap:9px}.paper-id{font-family:ui-monospace,Consolas,monospace;font-size:11px;color:var(--muted)}.copy-id{border:1px solid var(--line);background:none;border-radius:5px;font-size:10px;padding:1px 6px;color:var(--muted)}.read-select{border:1px solid var(--line);border-radius:6px;background:var(--surface);font-size:11px;padding:3px 7px;color:var(--muted)}.paper-card h3{font-size:19px;line-height:1.45;margin:11px 0 9px;overflow-wrap:anywhere}.paper-card h3 a{color:var(--ink)}.badges{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}.badge{font-size:11px;padding:2px 8px;border-radius:5px;background:#edf1ee;color:#47595d}.badge.accent{background:var(--light);color:var(--accent)}.badge.pending{background:#f6edd9;color:var(--amber)}.reason{font-size:13px;margin-bottom:12px;color:#354b52}.reason-label{font-weight:700;margin-right:6px;color:var(--ink)}.paper-links{display:flex;gap:16px;align-items:center;flex-wrap:wrap;font-size:12px;margin:10px 0}.details{border-top:1px solid var(--line);margin-top:14px;padding-top:11px}.details summary{cursor:pointer;color:var(--accent);font-size:12px;list-style-position:inside}.details[open] summary{margin-bottom:16px}.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px 25px}.detail-section{min-width:0}.detail-section.wide{grid-column:1/-1}.detail-section h4{font-size:12px;margin:0 0 6px;color:var(--muted);font-weight:600}.detail-section p,.detail-section ul{font-size:13px;margin:0;overflow-wrap:anywhere;white-space:pre-wrap}.detail-section ul{padding-left:18px}.detail-section li{margin-bottom:5px}.abstract{color:#53656a;max-height:280px;overflow:auto}.evidence{margin:10px 0 0;padding:12px 15px;border-left:3px solid #8db8ad;background:#f1f5ef;border-radius:0 7px 7px 0}.evidence blockquote{margin:0;color:#43585e;white-space:pre-wrap;font-size:12px;overflow-wrap:anywhere}.evidence cite{font-style:normal;font-size:11px;color:var(--muted);display:block;margin-top:7px}.question{background:#f5f3e9;border-radius:8px;padding:12px 14px}.empty{border:1px dashed #bbcbc4;border-radius:var(--radius);text-align:center;padding:52px 24px;background:var(--surface)}.empty h3{margin-bottom:7px}.empty p{color:var(--muted);font-size:13px}.empty button{border:1px solid var(--line);background:var(--light);border-radius:7px;padding:7px 14px;color:var(--accent)}footer{margin-top:32px;border-top:1px solid var(--line);padding-top:15px;color:var(--muted);font-size:11px;display:flex;justify-content:space-between;gap:20px}.status-toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--ink);color:white;padding:9px 18px;border-radius:8px;font-size:12px;box-shadow:0 4px 20px #172a3120;max-width:90vw;z-index:10}.hidden,[hidden]{display:none!important}
@media(min-width:901px){.filter-grid{grid-template-columns:1.3fr 1fr .9fr 1fr 1fr 1fr}}
@media(max-width:900px){.hero{grid-template-columns:1fr}.theme-grid{grid-template-columns:repeat(2,1fr)}.filter-grid{grid-template-columns:repeat(3,1fr)}.shell{padding:25px 22px 40px}.stats{gap:8px}.stat{padding:13px 12px}}
@media(max-width:600px){.shell{padding:20px 15px 36px}.masthead{margin-bottom:27px}.offline{font-size:10px}.hero{gap:20px}.interest{padding:16px}.stats{grid-template-columns:repeat(3,1fr)}.stat strong{font-size:22px}.theme-grid{grid-template-columns:1fr}.workbench{padding:18px 16px}.workbench-head{align-items:flex-start;flex-direction:column;gap:11px}.filter-grid{grid-template-columns:repeat(2,1fr);gap:10px}.paper-card{padding:18px 17px}.paper-card h3{font-size:17px}.detail-grid{grid-template-columns:1fr}.detail-section.wide{grid-column:auto}.paper-top{gap:10px;flex-wrap:wrap}.results-bar{align-items:flex-start}.card-index{gap:6px}footer{flex-direction:column;gap:6px}}
@media print{body{background:white}.shell{padding:0;max-width:none}.workbench,.copy-id,.read-select,.offline,.status-toast{display:none!important}.hero{grid-template-columns:1fr}.cards{display:block}.paper-card{break-inside:avoid;margin-bottom:15px}.details:not([open]){display:none}.stats{margin-top:15px}.paper-links a[href]:after{content:" (" attr(href) ")";font-size:9px;overflow-wrap:anywhere}}
</style>
</head>
<body>
<main class="shell">
  <div class="masthead"><div class="brand"><span class="brand-symbol" aria-hidden="true">◫</span><span>会议论文 · 研究阅读清单</span></div><span class="offline">离线可用</span></div>
  <section class="hero" aria-labelledby="report-title">
    <div><div class="eyebrow" id="report-mode"></div><h1 id="report-title"></h1><p class="lead" id="lead"></p><div class="hero-meta" id="metadata"></div></div>
    <aside class="interest" aria-label="本次研究兴趣"><h2>本次研究兴趣</h2><div id="interest-topics"></div></aside>
  </section>
  <section class="stats" aria-label="筛选覆盖情况" id="stats"></section>
  <p class="coverage-note" id="coverage-note"></p>
  <section class="overview" id="overview" hidden><div class="overview-heading"><h2>方向导读</h2><span class="section-kicker">按兴趣定位</span></div><div class="theme-grid" id="themes"></div></section>
  <section class="workbench" aria-labelledby="list-heading">
    <div class="workbench-head"><h2 id="list-heading">论文目录</h2><div class="segmented" role="group" aria-label="相关论文展示范围"><button type="button" id="view-selected">精选</button><button type="button" id="view-all">全部相关</button></div></div>
    <div class="search-wrap"><label for="search" aria-hidden="true">⌕</label><input id="search" type="search" placeholder="搜索标题、作者、方向、ID、推荐理由或摘要…" aria-label="搜索论文标题、作者、方向、ID、推荐理由、阅读建议或摘要" autocomplete="off"></div>
    <div class="filter-grid">
      <label>研究方向<select id="topic-filter"><option value="">全部方向</option></select></label>
      <label>关联类型<select id="relation-filter"><option value="">全部类型</option><option value="direct">直接相关</option><option value="method_transfer">方法可借鉴</option><option value="adjacent">邻近方向</option></select></label>
      <label>阅读优先级<select id="priority-filter"><option value="">全部优先级</option><option value="1">优先阅读</option><option value="2">补充阅读</option><option value="3">探索阅读</option></select></label>
      <label>记录状态<select id="status-filter"><option value="include">已推荐</option><option value="pending">待核查</option><option value="exclude">已排除</option><option value="unprocessed">未处理</option><option value="all">全部记录</option></select></label>
      <label>阅读标记<select id="reading-filter"><option value="">全部阅读状态</option><option value="unread">未读</option><option value="to_read">待读</option><option value="read">已读</option><option value="starred">重点关注</option></select></label>
      <label>排序<select id="sort-order"><option value="priority">优先级优先</option><option value="title">标题 A–Z</option><option value="id">固定 ID</option></select></label>
    </div>
    <div class="results-bar"><span id="result-count" role="status" aria-live="polite"></span><div><button type="button" class="clear-button" id="export-marks">导出阅读标记</button> · <button type="button" class="clear-button" id="clear-filters">重置筛选</button></div></div>
    <p class="reading-note" id="reading-note">阅读标记尝试保存在当前浏览器；不会自动同步到 JSON 或其他文档。</p>
  </section>
  <section class="cards" id="papers" aria-label="论文搜索结果"></section>
  <footer><span>相关性表示与本次兴趣的匹配程度。阅读优先级用于安排阅读顺序。</span><span>conference-paper-search · 本地阅读工具</span></footer>
</main>
<div class="status-toast" id="toast" role="status" aria-live="polite" hidden></div>
<script type="application/json" id="report-data">__BUNDLE_JSON__</script>
<script>
"use strict";
(() => {
const data = JSON.parse(document.getElementById("report-data").textContent);
const metadata = data.metadata || {}, coverage = data.coverage || {}, overview = data.overview || {};
const papers = Array.isArray(data.papers) ? data.papers : [];
const topics = Array.isArray((data.profile || {}).topics) ? data.profile.topics : [];
const topicById = new Map(topics.map(t => [String(t.id), t]));
const paperById = new Map(papers.map(p => [String(p.id), p]));
const relationNames = {direct:"直接相关", method_transfer:"方法可借鉴", adjacent:"邻近方向"};
const priorityNames = {1:"优先阅读", 2:"补充阅读", 3:"探索阅读"};
const stateNames = {include:"已推荐", pending:"待核查", exclude:"已排除", unprocessed:"未处理"};
const evidenceNames = {sufficient:"依据充分", limited:"依据有限", missing:"依据待补充"};
const acceptanceNames = {accepted:"已录用", rejected:"未录用", withdrawn:"已撤回", unknown:"录用状态未知"};
const relevanceNames = {high:"高相关", medium:"中相关", low:"低相关", unknown:"相关性待定"};
const $ = id => document.getElementById(id);
const list = value => Array.isArray(value) ? value : [];
const string = value => value == null ? "" : String(value);
const stateOf = p => p.assessment ? (p.assessment.decision || "unprocessed") : "unprocessed";
const rankOf = p => Number((p.assessment || {}).priority) || 4;
const idOf = p => string(p.display_id || p.id);
const recommendedOrder = new Map(list(metadata.recommended_ids).map((id,index)=>[string(id),index]));
const defaultSort = (a,b) => {
  const aIndex=recommendedOrder.get(string(a.id)), bIndex=recommendedOrder.get(string(b.id));
  if(aIndex != null || bIndex != null) return (aIndex == null ? Infinity : aIndex)-(bIndex == null ? Infinity : bIndex);
  return rankOf(a)-rankOf(b) || idOf(a).localeCompare(idOf(b));
};
const topK = Math.max(1, Number(metadata.top_k) || 20);
const included = papers.filter(p => stateOf(p) === "include").sort(defaultSort);
const selectedIds = new Set(Array.isArray(metadata.selected_ids) ? metadata.selected_ids : included.slice(0,topK).map(p => p.id));
let view = metadata.mode === "attend" ? "selected" : "all";
let toastTimer = null;
const storageKey = "conference-paper-search:v1:" + [metadata.conference,metadata.year,metadata.source_url].map(string).join("|");
let readingMarks = {}, storageAvailable = true;
try { readingMarks = JSON.parse(localStorage.getItem(storageKey) || "{}"); if (!readingMarks || typeof readingMarks !== "object" || Array.isArray(readingMarks)) readingMarks = {}; }
catch (_) { storageAvailable = false; }
if (!storageAvailable) $("reading-note").textContent = "当前浏览器不支持保存阅读标记；本次打开期间可以使用，关闭后可能丢失。标记不会自动同步到其他文档。";

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = string(text);
  return node;
}
function safeUrl(raw) {
  if (typeof raw !== "string" || !raw || /[\s\u0000-\u001f\u007f]/.test(raw)) return null;
  try { const url = new URL(raw); return ["http:","https:"].includes(url.protocol) && !url.username && !url.password && url.hostname ? url.href : null; }
  catch (_) { return null; }
}
function link(label, raw) {
  const url = safeUrl(raw);
  if (!url) return null;
  const node = element("a", "", label); node.href = url; node.target = "_blank"; node.rel = "noopener noreferrer"; return node;
}
function addLink(parent, label, raw) { const node = link(label,raw); if (node) parent.append(node); }
function appendBadge(parent, text, type) { if (text) parent.append(element("span","badge" + (type ? " " + type : ""),text)); }
function showToast(message) {
  const toast = $("toast"); toast.textContent = message; toast.hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => { toast.hidden = true; },2600);
}
async function copyId(p) {
  const text = idOf(p);
  try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); showToast("已复制 " + text); return; } } catch (_) {}
  const helper = element("textarea","",text); helper.style.position="fixed"; helper.style.left="-9999px"; document.body.append(helper); helper.select();
  let copied = false; try { copied = document.execCommand("copy"); } catch (_) {} helper.remove();
  if (copied) showToast("已复制 " + text); else window.prompt("复制固定 ID：",text);
}
function topicName(id) { const topic = topicById.get(string(id)); return topic ? string(topic.problem || topic.id) : string(id); }
function labelsFor(p) { const labels = list(p.topic_labels); return labels.length ? labels.map(string) : list((p.assessment || {}).topic_ids).map(topicName); }
function section(parent, heading, value, wide) {
  if (value == null || value === "" || (Array.isArray(value) && !value.length)) return;
  const node = element("div","detail-section" + (wide ? " wide" : "")); node.append(element("h4","",heading));
  if (Array.isArray(value)) { const ul=element("ul"); value.forEach(item=>ul.append(element("li","",item))); node.append(ul); }
  else node.append(element("p","",value)); parent.append(node); return node;
}
function saveMark(p, value) {
  readingMarks[p.id] = value;
  try { localStorage.setItem(storageKey,JSON.stringify(readingMarks)); }
  catch (_) { storageAvailable = false; $("reading-note").textContent = "阅读标记仅在本次打开期间保留；浏览器未能保存。标记不会自动同步到 JSON 或其他文档。"; }
  if ($("reading-filter").value) render();
}

const conferenceTitle = [metadata.conference_label || metadata.conference,metadata.year].filter(v=>v != null && v !== "").join(" ") || "会议论文";
$("report-title").textContent = conferenceTitle;
$("report-mode").textContent = metadata.mode === "attend" ? "参会阅读清单" : "会后方向总结";
$("lead").textContent = overview.lead || (metadata.mode === "attend" ? "按研究兴趣定位优先阅读的论文，核对推荐依据，并在官方日程已验证时查看展示信息。" : "按研究兴趣查看本次范围内的相关工作，沿子方向浏览论文，并展开推荐依据与阅读建议。");
const metaNode = $("metadata");
metaNode.append(element("span","", "范围：" + (metadata.track === "main" ? "主会" : string(metadata.track || "未指定"))));
if (metadata.retrieved_at) metaNode.append(element("span","","获取日期：" + string(metadata.retrieved_at).slice(0,10)));
addLink(metaNode,"官方来源",metadata.source_url);
const interestNode = $("interest-topics");
if (!topics.length) interestNode.append(element("p","","未提供研究兴趣描述。"));
topics.forEach(t => {
  const node = element("div","interest-item"); node.append(element("strong","",t.problem || t.id));
  if (list(t.focus).length) node.append(element("p","","关注："+t.focus.join(" · ")));
  if (list(t.constraints).length) node.append(element("p","","约束："+t.constraints.join("；")));
  if (list(t.exclude).length) node.append(element("p","","暂不关注："+t.exclude.join("；")));
  const provenance = list(t.provenance).map(x=>x.kind === "user" ? "用户描述" : x.kind === "publication_inference" ? "论文推断" : string(x.kind)).filter(Boolean);
  if (provenance.length) node.append(element("p","","方向来源："+Array.from(new Set(provenance)).join("、")));
  interestNode.append(node);
});
const countState = state => papers.filter(p=>stateOf(p)===state).length;
const total = coverage.total_papers == null ? papers.length : coverage.total_papers;
const processed = coverage.processed == null ? papers.length-countState("unprocessed") : coverage.processed;
const counts = [
  [total,"本次范围论文",""],
  [coverage.included == null ? countState("include") : coverage.included,"已推荐","primary"],
  [coverage.pending == null ? countState("pending") : coverage.pending,"待核查",""],
  [coverage.unprocessed == null ? countState("unprocessed") : coverage.unprocessed,"未处理",""],
  [coverage.excluded == null ? countState("exclude") : coverage.excluded,"已排除",""]
];
counts.forEach(([n,label,style])=>{ const stat=element("div","stat"+(style?" "+style:""));stat.append(element("strong","",n),element("span","",label));$("stats").append(stat); });
const notes = [metadata.scope_note, "已处理 " + processed + " 篇。未处理与待核查均不等于不相关；默认目录展示已推荐论文。"].filter(Boolean);
const missingAbstracts = coverage.missing_abstract == null ? papers.filter(p=>!p.abstract).length : coverage.missing_abstract;
if (missingAbstracts) notes.push("缺失摘要 " + missingAbstracts + " 篇。");
$("coverage-note").textContent = notes.join(" ");
topics.forEach(t=>{ const opt=element("option","",t.problem||t.id);opt.value=string(t.id);$("topic-filter").append(opt); });
const themeList = list(overview.themes);
if (themeList.length) {
  $("overview").hidden=false;
  themeList.forEach(theme=>{
    const card=element("article","theme");card.append(element("h3","",topicName(theme.topic_id)),element("p","",theme.text));
    const refs=element("div","inline-ids");
    list(theme.paper_ids).forEach(id=>{const p=paperById.get(string(id));if(!p)return;const b=element("button","text-button",idOf(p));b.type="button";b.title=string(p.title);b.addEventListener("click",()=>jumpToPaper(p));refs.append(b);});
    if(refs.childNodes.length)card.append(refs);$("themes").append(card);
  });
}
const questions = new Map(list(overview.attendance_questions).map(q=>[string(q.paper_id),list(q.questions)]));
function makeCard(p) {
  const a = p.assessment || {}, state=stateOf(p);
  const card=element("article","paper-card"); card.id="paper-"+encodeURIComponent(string(p.id));
  const top=element("div","paper-top"), index=element("div","card-index");
  index.append(element("span","paper-id",idOf(p)));
  const copy=element("button","copy-id","复制 ID");copy.type="button";copy.setAttribute("aria-label","复制论文 "+idOf(p)+" 的固定 ID");copy.addEventListener("click",()=>copyId(p));index.append(copy);top.append(index);
  const read=element("select","read-select");read.setAttribute("aria-label",idOf(p)+" 的阅读标记");
  [["unread","未读"],["to_read","待读"],["read","已读"],["starred","重点关注"]].forEach(([value,label])=>{const opt=element("option","",label);opt.value=value;read.append(opt);});
  const stored=readingMarks[p.id] || p.reading_status;read.value=["unread","to_read","read","starred"].includes(stored)?stored:"unread";read.addEventListener("change",()=>saveMark(p,read.value));top.append(read);card.append(top);
  const heading=element("h3"), titleLink=link(p.title,p.url);heading.append(titleLink || element("span","",p.title));card.append(heading);
  const badges=element("div","badges");
  if(state!=="include")appendBadge(badges,stateNames[state]||state,state==="pending"?"pending":"");
  appendBadge(badges,relationNames[a.relation],"accent");appendBadge(badges,priorityNames[a.priority],a.priority===1?"accent":"");
  labelsFor(p).forEach(label=>appendBadge(badges,label));
  if(badges.childNodes.length)card.append(badges);
  const reason=element("p","reason");reason.append(element("span","reason-label",state==="include"?"推荐理由":state==="exclude"?"排除理由":state==="pending"?"待核查说明":"处理状态"),element("span","",a.reason || "这篇论文尚未进行相关性评估。"));card.append(reason);
  const links=element("div","paper-links");addLink(links,"论文页面 ↗",p.url);addLink(links,"论文全文 ↗",p.pdf_url);if(links.childNodes.length)card.append(links);
  const details=element("details","details");details.append(element("summary","","展开研究内容、推荐依据与阅读建议"));
  const grid=element("div","detail-grid");
  section(grid,"作者",list(p.authors).length?p.authors.join(" · "):"作者信息未提供。",true);
  section(grid,"匹配的研究方向",list(a.topic_ids).map(topicName));
  const statusText = [acceptanceNames[p.acceptance] || "录用状态未知",relevanceNames[a.relevance],evidenceNames[a.evidence_status]].filter(Boolean).join(" · ");section(grid,"判断状态",statusText);
  section(grid,"重点阅读",a.reading_focus || (state==="unprocessed"?"需要先阅读资料并评估相关性。":""));
  section(grid,"个人备注",p.user_notes,true);
  section(grid,"关键差异",list(a.differences));section(grid,"待核查事项",list(a.uncertainties));
  const abstractSection=section(grid,"摘要",p.abstract || "摘要尚未获取；请查看论文页面或全文。",true);if(abstractSection)abstractSection.lastChild.classList.add("abstract");
  const sourceById=new Map(list(p.sources).map(source=>[string(source.id),source]));
  if(list(a.evidence).length){
    const ev=element("div","detail-section wide");ev.append(element("h4","","可核查的原文依据"));
    a.evidence.forEach(e=>{
      const source=sourceById.get(string(e.source_id))||{},block=element("div","evidence");block.append(element("blockquote","",e.quote));
      const cite=element("cite","",[source.kind==="abstract"?"摘要":source.kind==="full_text"?"正文":source.kind==="title"?"标题":e.source_id,source.locator].filter(Boolean).join(" · ")+" ");addLink(cite,"查看来源 ↗",source.url);block.append(cite);ev.append(block);
    });grid.append(ev);
  }
  const presentation=p.presentation;
  if(presentation && presentation.confirmed===true && safeUrl(presentation.source_url)){
    const schedule=section(grid,"已核实的展示信息",[presentation.time,presentation.timezone,presentation.session,presentation.location].filter(Boolean).join(" · ") || "展示信息已核实；具体时间与地点未提供。",true);
    if(schedule){const source=element("p");addLink(source,"官方日程 ↗",presentation.source_url);schedule.append(source);}
  } else if(metadata.mode==="attend")section(grid,"展示信息","官方展示时间、场次和地点尚未核实。论文录用不代表作者将现场到场。",true);
  const qs=questions.get(string(p.id));if(qs && qs.length){const q=section(grid,"可讨论的问题",qs,true);if(q)q.classList.add("question");}
  details.append(grid);card.append(details);return card;
}
function searchText(p) {
  const a=p.assessment||{};
  const schedule=p.presentation && p.presentation.confirmed===true?p.presentation:{};
  return [p.title,...list(p.authors),idOf(p),p.id,...labelsFor(p),a.reason,a.reading_focus,p.abstract,...list(a.differences),...list(a.uncertainties),schedule.time,schedule.timezone,schedule.session,schedule.location].map(string).join(" ").toLocaleLowerCase();
}
const searchIndex=new Map(papers.map(p=>[p.id,searchText(p)]));
function render() {
  $("view-selected").setAttribute("aria-pressed",string(view==="selected"));$("view-all").setAttribute("aria-pressed",string(view==="all"));
  const state=$("status-filter").value,topic=$("topic-filter").value,relation=$("relation-filter").value,priority=$("priority-filter").value,reading=$("reading-filter").value;
  const terms=$("search").value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  const pool=papers.filter(p=>state==="all" || stateOf(p)===state).filter(p=>state!=="include" || view!=="selected" || selectedIds.has(p.id));
  let results=pool.filter(p=>{
    const a=p.assessment||{};
    return (!topic || list(a.topic_ids).map(string).includes(topic)) && (!relation || a.relation===relation) && (!priority || string(a.priority)===priority) && (!reading || (readingMarks[p.id] || p.reading_status || "unread")===reading) && terms.every(term=>searchIndex.get(p.id).includes(term));
  });
  const sort=$("sort-order").value;
  results.sort(sort==="title"?(a,b)=>string(a.title).localeCompare(string(b.title)):sort==="id"?(a,b)=>idOf(a).localeCompare(idOf(b)):defaultSort);
  const scope=state==="include"?(view==="selected"?"精选 "+Math.min(topK,included.length)+" 篇":"全部相关 "+included.length+" 篇"):state==="all"?"全部记录 "+papers.length+" 篇":(stateNames[state]||state)+" "+pool.length+" 篇";
  $("result-count").textContent="显示 "+results.length+" / "+pool.length+" 篇 · "+scope;
  $("view-selected").disabled=state!=="include";$("view-all").disabled=state!=="include";
  const container=$("papers");container.replaceChildren();
  if(!results.length){
    const empty=element("div","empty");empty.append(element("h3","","当前条件下没有论文"),element("p","",pool.length?"可以减少搜索词、调整筛选条件，或切换到全部相关论文。":"当前记录状态没有论文。可切换记录状态查看其他材料。"));
    const reset=element("button","","重置筛选并查看全部相关");reset.type="button";reset.addEventListener("click",()=>resetFilters("all"));empty.append(reset);container.append(empty);
  }else{const fragment=document.createDocumentFragment();results.forEach(p=>fragment.append(makeCard(p)));container.append(fragment);}
}
function resetFilters(nextView) {
  $("search").value="";$("topic-filter").value="";$("relation-filter").value="";$("priority-filter").value="";$("reading-filter").value="";$("status-filter").value="include";$("sort-order").value="priority";
  view=nextView || (metadata.mode==="attend"?"selected":"all");render();
}
function jumpToPaper(p){resetFilters("all");$("status-filter").value=stateOf(p);$("search").value=idOf(p);render();const card=document.getElementById("paper-"+encodeURIComponent(string(p.id)));if(card){card.querySelector("details").open=true;card.scrollIntoView({behavior:"smooth",block:"start"});}}
$("view-selected").textContent="精选 "+Math.min(topK,included.length)+" 篇";
$("view-selected").addEventListener("click",()=>{view="selected";render();});$("view-all").addEventListener("click",()=>{view="all";render();});
$("search").addEventListener("input",render);
["topic-filter","relation-filter","priority-filter","reading-filter","status-filter","sort-order"].forEach(id=>$(id).addEventListener("change",render));
$("clear-filters").addEventListener("click",()=>resetFilters());
$("export-marks").addEventListener("click",()=>{
  const marks={schema_version:"1.0",kind:"reading_marks",conference:metadata.conference,year:metadata.year,records:papers.map(p=>({paper_id:p.id,display_id:idOf(p),reading_status:readingMarks[p.id] || p.reading_status || "unread"}))};
  const blob=new Blob([JSON.stringify(marks,null,2)],{type:"application/json;charset=utf-8"});
  const url=URL.createObjectURL(blob),download=element("a");download.href=url;download.download="reading-marks.json";document.body.append(download);download.click();download.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
function openHashTarget(){
  let target;try{target=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
  if(!target)return;const paper=papers.find(p=>idOf(p)===target || string(p.id)===target);if(paper)jumpToPaper(paper);
}
window.addEventListener("hashchange",openHashTarget);
render();
openHashTarget();
})();
</script>
</body>
</html>
'''
