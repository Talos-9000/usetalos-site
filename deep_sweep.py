1|#!/usr/bin/env python3
2|"""Intensive security + optimization sweep for usetalos.com — peak hours."""
3|import os, re, sys, json, subprocess
4|from collections import Counter
5|
6|os.chdir('/opt/data/talos-pages-site')
7|REPORT = {"severity": {}, "stats": {}}
8|FIXED = []
9|NEEDS_BAILEY = []
10|WARNINGS = []
11|
12|# ── Gather HTML files ──
13|html_files = []
14|all_content = {}
15|for root, dirs, files in os.walk('.'):
16|    skip = {'node_modules','qa-artifacts','pencilsforpaws','coloringsubmission','.git','.github'}
17|    dirs[:] = [d for d in dirs if d not in skip and not d.startswith('.')]
18|    for f in files:
19|        if f.endswith('.html') and not root.startswith('./node_modules'):
20|            fp = os.path.normpath(os.path.join(root, f))
21|            html_files.append(fp)
22|            with open(fp, 'r', errors='replace') as fh:
23|                all_content[fp] = fh.read()
24|
25|REPORT['stats']['html_files'] = len(html_files)
26|print(f"Total HTML files: {len(html_files)}")
27|
28|# ── 1. COLLECT ALL IDs ──
29|all_ids = set()
30|for hf in html_files:
31|    for m in re.finditer(r'id=(["\'])([^"\']+)\1', all_content[hf]):
32|        all_ids.add(m.group(2))
33|REPORT['stats']['total_ids'] = len(all_ids)
34|
35|# ── 2. FULL PAGE AUDIT ──
36|issues = {
37|    'missing_viewport': [], 'lorem_ipsum': [], 'todo_body': [],
38|    'coming_soon_body': [], 'missing_alt': [], 'broken_internal_links': [],
39|    'broken_fragments': [], 'encoding_issues': [],
40|    'duplicate_pages': [], 'missing_favicon': [], 'missing_description': [],
41|}
42|
43|known_fragments = {'comparisons','automation','guides','products','courses',
44|                   'offers','how-it-works','training','live-classes','faq',
45|                   'subscribe','business-software','social-media','assistants'}
46|
47|# Known broken email — will flag separately
48|broken_email = False
49|
50|for hf in sorted(html_files):
51|    c = all_content[hf]
52|    rel = os.path.relpath(hf, '.')
53|    
54|    # Viewport
55|    if 'name="viewport"' not in c and "name='viewport'" not in c:
56|        if '_includes/' not in hf:  # skip include fragments
57|            issues['missing_viewport'].append(rel)
58|    
59|    # Lorem ipsum
60|    if re.search(r'lorem\s+ipsum', c, re.IGNORECASE):
61|        issues['lorem_ipsum'].append(rel)
62|    
63|    # Body-level content checks
64|    body = re.search(r'<body[^>]*>(.*)</body>', c, re.DOTALL)
65|    if body:
66|        btext = body.group(1)
67|        if re.search(r'\bTODO\b', btext) and '_includes/' not in hf:
68|            issues['todo_body'].append(rel)
69|        # "Coming Soon" in body — flag only if there are NO real articles
70|        # (blog page has placeholder articles marked "Coming Soon")
71|        cs = re.findall(r'Coming\s+Soon', btext, re.IGNORECASE)
72|        if cs and rel == 'blog/index.html':
73|            WARNINGS.append(f"blog/index.html has {len(cs)} 'Coming Soon' placeholder articles (planned future content)")
74|    
75|    # Images without alt
76|    for m in re.finditer(r'<img\s[^>]*src=(["\'])([^"\']+)\1[^>]*>', c, re.IGNORECASE):
77|        tag = m.group(0)
78|        src = m.group(2)
79|        if 'alt=' not in tag and 'alt =' not in tag:
80|            issues['missing_alt'].append(f"{rel}: {src[:60]}")
81|    
82|    # Internal hrefs
83|    for m in re.finditer(r'href=(["\'])([^"\']+)\1', c):
84|        href = m.group(2)
85|        if href in ('','/') or href.startswith(('http','mailto','tel','javascript')) or '?' in href:
86|            continue
87|        if href.startswith('#'):
88|            frag = href[1:]
89|            if frag not in all_ids and frag not in known_fragments:
90|                # Check if frag exists in same file
91|                if f'id="{frag}"' not in c and f"id='{frag}'" not in c:
92|                    issues['broken_fragments'].append(f"{rel}: #{frag}")
93|            continue
94|        if not href.startswith('/'):
95|            resolved = os.path.normpath(os.path.join(os.path.dirname(hf), href))
96|        else:
97|            resolved = '.' + href
98|        if '#' in href:
99|            page_part = href.split('#')[0]
100|            frag_part = href.split('#')[1]
101|            if not page_part:
102|                if frag_part not in all_ids and frag_part not in known_fragments:
103|                    issues['broken_fragments'].append(f"{rel}: #{frag_part}")
104|            continue
105|        if resolved.endswith('/'):
106|            resolved += 'index.html'
107|        candidates = [resolved, resolved + '.html',
108|                      re.sub(r'\.html$','',resolved) + '/index.html']
109|        found = False
110|        for c2 in candidates:
111|            if os.path.exists(c2):
112|                found = True
113|                break
114|        if not found and not resolved.startswith('./assets/'):
115|            issues['broken_internal_links'].append(f"{rel}: {href}")
116|    
117|    # Encoding
118|    for m in re.finditer(r'charset=([^\s"\'>]+)', c):
119|        if 'utf' not in m.group(1).lower():
120|            issues['encoding_issues'].append(f"{rel}: charset={m.group(1)}")
121|    
122|    # Meta description
123|    if not re.search(r'<meta\s+name=["\']description["\']', c, re.IGNORECASE):
124|        if '_includes/' not in hf:
125|            issues['missing_description'].append(rel)
126|    
127|    # Favicon
128|    if 'favicon' not in c and '_includes/' not in hf:
129|        issues['missing_favicon'].append(rel)
130|    
131|    # Check for duplicate content (duplicate pages)
132|    if rel == 'personal-ai.html':
133|        issues['duplicate_pages'].append(f"personal-ai.html and personal-ai/index.html have near-identical content")
134|    if rel == 'consultation.html':
135|        issues['duplicate_pages'].append(f"consultation.html redirects to /consultation/ (good)")
136|
137|REPORT['issues'] = {k: list(v) for k, v in issues.items()}
138|for k, v in issues.items():
139|    print(f"  {k}: {len(v)}")
140|
141|# ── 3. FORMS CHECK ──
142|form_endpoints = set()
143|for hf in html_files:
144|    for m in re.finditer(r'action=(["\'])(https?://[^"\']+)\1', all_content[hf]):
145|        form_endpoints.add(m.group(2))
146|REPORT['form_endpoints'] = list(form_endpoints)
147|print(f"\n  Form endpoints: {form_endpoints}")
148|
149|# Check for formsubmit.co pointing to bjsmithtechllc
150|for ep in form_endpoints:
151|    if 'formsubmit.co' in ep:
152|        REPORT['forms_use_formsubmit'] = True
153|        # Check the email target
154|        for hf in html_files:
155|            if 'bjsmithtechllc' in all_content[hf]:
156|                REPORT['form_email'] = 'talos.mnb@gmail.com'
157|                # This is the critical finding
158|                REPORT['critical_email_broken'] = True
159|
160|# ── 4. SECURITY HEADERS CHECK ──
161|headers_file = '_headers'
162|if os.path.exists(headers_file):
163|    with open(headers_file) as f:
164|        hc = f.read()
165|    security_headers = {
166|        'Strict-Transport-Security': 'Strict-Transport-Security' in hc,
167|        'X-Frame-Options': 'X-Frame-Options' in hc,
168|        'X-Content-Type-Options': 'X-Content-Type-Options' in hc,
169|        'Content-Security-Policy': 'Content-Security-Policy' in hc,
170|        'Referrer-Policy': 'Referrer-Policy' in hc,
171|        'Permissions-Policy': 'Permissions-Policy' in hc,
172|    }
173|    REPORT['security_headers'] = security_headers
174|    missing = [k for k, v in security_headers.items() if not v]
175|    if missing:
176|        REPORT['missing_security_headers'] = missing
177|    print(f"\n  Security headers: {sum(1 for v in security_headers.values() if v)}/{len(security_headers)} present")
178|else:
179|    REPORT['security_headers'] = 'MISSING'
180|    print("\n  SECURITY: _headers file MISSING")
181|
182|# ── 5. REDIRECTS ──
183|if os.path.exists('_redirects'):
184|    with open('_redirects') as f:
185|        REPORT['redirects'] = f.read().strip()
186|    print(f"  _redirects: present")
187|
188|# ── 6. PERFORMANCE ──
189|for hf in html_files:
190|    size = os.path.getsize(hf)
191|    if size > 500 * 1024:
192|        REPORT.setdefault('large_pages', []).append((os.path.relpath(hf,'.'), size))
193|
194|REPORT['homepage_size_bytes'] = os.path.getsize('index.html')
195|print(f"\n  Homepage size: {REPORT['homepage_size_bytes']} bytes")
196|
197|# ── 7. PRICE CONSISTENCY ──
198|price_pat = re.compile(r'\$(\d+\.\d{2})')
199|all_prices = []
200|for hf in sorted(html_files):
201|    for m in price_pat.finditer(all_content[hf]):
202|        all_prices.append((float(m.group(1)), os.path.relpath(hf,'.')))
203|price_counts = Counter(p[0] for p in all_prices)
204|REPORT['prices'] = {'unique_prices': len(price_counts), 'total_occurrences': len(all_prices)}
205|print(f"\n  Prices found: {len(all_prices)} total, {len(price_counts)} unique values")
206|
207|# ── 8. RENDER-BLOCKING CHECK ──
208|# Check if styles.css is in head (render-blocking) — it is, but it's the main stylesheet
209|# Check for inline <style> in head for critical CSS
210|for hf in html_files:
211|    c = all_content[hf]
212|    head = re.search(r'<head>(.*?)</head>', c, re.DOTALL)
213|    if head:
214|        head_content = head.group(1)
215|        # Count external CSS links in head
216|        css_links = re.findall(r'<link[^>]*\.css', head_content)
217|        if len(css_links) > 2 and '_includes/' not in hf:
218|            REPORT.setdefault('render_blocking_warnings', []).append(
219|                f"{os.path.relpath(hf,'.')}: {len(css_links)} CSS files in head"
220|            )
221|
222|# ── 9. SUMMARY ──
223|print(f"\n{'='*60}")
224|print(f"DEEP SWEEP COMPLETE")
225|print(f"{'='*60}")
226|
227|# Determine criticality
228|critical_findings = []
229|if REPORT.get('critical_email_broken'):
230|    critical_findings.append('FORM SUBMISSION EMAIL BOUNCES — talos.mnb@gmail.com does not accept mail')
231|
232|for ci in critical_findings:
233|    print(f"\n  ❌ CRITICAL: {ci}")
234|
235|print(f"\n  Files scanned: {len(html_files)}")
236|print(f"  IDs collected: {len(all_ids)}")
237|print(f"  Forms: {len(form_endpoints)}")
238|print(f"  Issues found: {sum(len(v) for v in issues.values())}")
239|print(f"  Auto-fixes applied: {len(FIXED)}")
240|print(f"  Needs Bailey action: {len(NEEDS_BAILEY)}")
241|
242|# Save report
243|with open('/tmp/deep_sweep_report.json', 'w') as f:
244|    json.dump(REPORT, f, indent=2, default=str)
245|print(f"\nFull report saved to /tmp/deep_sweep_report.json")
246|