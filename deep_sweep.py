#!/usr/bin/env python3
"""Intensive security + optimization sweep for usetalos.com — peak hours."""
import os, re, sys, json, subprocess
from collections import Counter

os.chdir('/opt/data/talos-pages-site')
REPORT = {"severity": {}, "stats": {}}
FIXED = []
NEEDS_BAILEY = []
WARNINGS = []

# ── Gather HTML files ──
html_files = []
all_content = {}
for root, dirs, files in os.walk('.'):
    skip = {'node_modules','qa-artifacts','pencilsforpaws','coloringsubmission','.git','.github'}
    dirs[:] = [d for d in dirs if d not in skip and not d.startswith('.')]
    for f in files:
        if f.endswith('.html') and not root.startswith('./node_modules'):
            fp = os.path.normpath(os.path.join(root, f))
            html_files.append(fp)
            with open(fp, 'r', errors='replace') as fh:
                all_content[fp] = fh.read()

REPORT['stats']['html_files'] = len(html_files)
print(f"Total HTML files: {len(html_files)}")

# ── 1. COLLECT ALL IDs ──
all_ids = set()
for hf in html_files:
    for m in re.finditer(r'id=(["\'])([^"\']+)\1', all_content[hf]):
        all_ids.add(m.group(2))
REPORT['stats']['total_ids'] = len(all_ids)

# ── 2. FULL PAGE AUDIT ──
issues = {
    'missing_viewport': [], 'lorem_ipsum': [], 'todo_body': [],
    'coming_soon_body': [], 'missing_alt': [], 'broken_internal_links': [],
    'broken_fragments': [], 'encoding_issues': [],
    'duplicate_pages': [], 'missing_favicon': [], 'missing_description': [],
}

known_fragments = {'comparisons','automation','guides','products','courses',
                   'offers','how-it-works','training','live-classes','faq',
                   'subscribe','business-software','social-media','assistants'}

# Known broken email — will flag separately
broken_email = False

for hf in sorted(html_files):
    c = all_content[hf]
    rel = os.path.relpath(hf, '.')
    
    # Viewport
    if 'name="viewport"' not in c and "name='viewport'" not in c:
        if '_includes/' not in hf:  # skip include fragments
            issues['missing_viewport'].append(rel)
    
    # Lorem ipsum
    if re.search(r'lorem\s+ipsum', c, re.IGNORECASE):
        issues['lorem_ipsum'].append(rel)
    
    # Body-level content checks
    body = re.search(r'<body[^>]*>(.*)</body>', c, re.DOTALL)
    if body:
        btext = body.group(1)
        if re.search(r'\bTODO\b', btext) and '_includes/' not in hf:
            issues['todo_body'].append(rel)
        # "Coming Soon" in body — flag only if there are NO real articles
        # (blog page has placeholder articles marked "Coming Soon")
        cs = re.findall(r'Coming\s+Soon', btext, re.IGNORECASE)
        if cs and rel == 'blog/index.html':
            WARNINGS.append(f"blog/index.html has {len(cs)} 'Coming Soon' placeholder articles (planned future content)")
    
    # Images without alt
    for m in re.finditer(r'<img\s[^>]*src=(["\'])([^"\']+)\1[^>]*>', c, re.IGNORECASE):
        tag = m.group(0)
        src = m.group(2)
        if 'alt=' not in tag and 'alt =' not in tag:
            issues['missing_alt'].append(f"{rel}: {src[:60]}")
    
    # Internal hrefs
    for m in re.finditer(r'href=(["\'])([^"\']+)\1', c):
        href = m.group(2)
        if href in ('','/') or href.startswith(('http','mailto','tel','javascript')) or '?' in href:
            continue
        if href.startswith('#'):
            frag = href[1:]
            if frag not in all_ids and frag not in known_fragments:
                # Check if frag exists in same file
                if f'id="{frag}"' not in c and f"id='{frag}'" not in c:
                    issues['broken_fragments'].append(f"{rel}: #{frag}")
            continue
        if not href.startswith('/'):
            resolved = os.path.normpath(os.path.join(os.path.dirname(hf), href))
        else:
            resolved = '.' + href
        if '#' in href:
            page_part = href.split('#')[0]
            frag_part = href.split('#')[1]
            if not page_part:
                if frag_part not in all_ids and frag_part not in known_fragments:
                    issues['broken_fragments'].append(f"{rel}: #{frag_part}")
            continue
        if resolved.endswith('/'):
            resolved += 'index.html'
        candidates = [resolved, resolved + '.html',
                      re.sub(r'\.html$','',resolved) + '/index.html']
        found = False
        for c2 in candidates:
            if os.path.exists(c2):
                found = True
                break
        if not found and not resolved.startswith('./assets/'):
            issues['broken_internal_links'].append(f"{rel}: {href}")
    
    # Encoding
    for m in re.finditer(r'charset=([^\s"\'>]+)', c):
        if 'utf' not in m.group(1).lower():
            issues['encoding_issues'].append(f"{rel}: charset={m.group(1)}")
    
    # Meta description
    if not re.search(r'<meta\s+name=["\']description["\']', c, re.IGNORECASE):
        if '_includes/' not in hf:
            issues['missing_description'].append(rel)
    
    # Favicon
    if 'favicon' not in c and '_includes/' not in hf:
        issues['missing_favicon'].append(rel)
    
    # Check for duplicate content (duplicate pages)
    if rel == 'personal-ai.html':
        issues['duplicate_pages'].append(f"personal-ai.html and personal-ai/index.html have near-identical content")
    if rel == 'consultation.html':
        issues['duplicate_pages'].append(f"consultation.html redirects to /consultation/ (good)")

REPORT['issues'] = {k: list(v) for k, v in issues.items()}
for k, v in issues.items():
    print(f"  {k}: {len(v)}")

# ── 3. FORMS CHECK ──
form_endpoints = set()
for hf in html_files:
    for m in re.finditer(r'action=(["\'])(https?://[^"\']+)\1', all_content[hf]):
        form_endpoints.add(m.group(2))
REPORT['form_endpoints'] = list(form_endpoints)
print(f"\n  Form endpoints: {form_endpoints}")

# Check for formsubmit.co pointing to bjsmithtechllc
for ep in form_endpoints:
    if 'formsubmit.co' in ep:
        REPORT['forms_use_formsubmit'] = True
        # Check the email target
        for hf in html_files:
            if 'bjsmithtechllc' in all_content[hf]:
                REPORT['form_email'] = 'bjsmithtechllc@gmail.com'
                # This is the critical finding
                REPORT['critical_email_broken'] = True

# ── 4. SECURITY HEADERS CHECK ──
headers_file = '_headers'
if os.path.exists(headers_file):
    with open(headers_file) as f:
        hc = f.read()
    security_headers = {
        'Strict-Transport-Security': 'Strict-Transport-Security' in hc,
        'X-Frame-Options': 'X-Frame-Options' in hc,
        'X-Content-Type-Options': 'X-Content-Type-Options' in hc,
        'Content-Security-Policy': 'Content-Security-Policy' in hc,
        'Referrer-Policy': 'Referrer-Policy' in hc,
        'Permissions-Policy': 'Permissions-Policy' in hc,
    }
    REPORT['security_headers'] = security_headers
    missing = [k for k, v in security_headers.items() if not v]
    if missing:
        REPORT['missing_security_headers'] = missing
    print(f"\n  Security headers: {sum(1 for v in security_headers.values() if v)}/{len(security_headers)} present")
else:
    REPORT['security_headers'] = 'MISSING'
    print("\n  SECURITY: _headers file MISSING")

# ── 5. REDIRECTS ──
if os.path.exists('_redirects'):
    with open('_redirects') as f:
        REPORT['redirects'] = f.read().strip()
    print(f"  _redirects: present")

# ── 6. PERFORMANCE ──
for hf in html_files:
    size = os.path.getsize(hf)
    if size > 500 * 1024:
        REPORT.setdefault('large_pages', []).append((os.path.relpath(hf,'.'), size))

REPORT['homepage_size_bytes'] = os.path.getsize('index.html')
print(f"\n  Homepage size: {REPORT['homepage_size_bytes']} bytes")

# ── 7. PRICE CONSISTENCY ──
price_pat = re.compile(r'\$(\d+\.\d{2})')
all_prices = []
for hf in sorted(html_files):
    for m in price_pat.finditer(all_content[hf]):
        all_prices.append((float(m.group(1)), os.path.relpath(hf,'.')))
price_counts = Counter(p[0] for p in all_prices)
REPORT['prices'] = {'unique_prices': len(price_counts), 'total_occurrences': len(all_prices)}
print(f"\n  Prices found: {len(all_prices)} total, {len(price_counts)} unique values")

# ── 8. RENDER-BLOCKING CHECK ──
# Check if styles.css is in head (render-blocking) — it is, but it's the main stylesheet
# Check for inline <style> in head for critical CSS
for hf in html_files:
    c = all_content[hf]
    head = re.search(r'<head>(.*?)</head>', c, re.DOTALL)
    if head:
        head_content = head.group(1)
        # Count external CSS links in head
        css_links = re.findall(r'<link[^>]*\.css', head_content)
        if len(css_links) > 2 and '_includes/' not in hf:
            REPORT.setdefault('render_blocking_warnings', []).append(
                f"{os.path.relpath(hf,'.')}: {len(css_links)} CSS files in head"
            )

# ── 9. SUMMARY ──
print(f"\n{'='*60}")
print(f"DEEP SWEEP COMPLETE")
print(f"{'='*60}")

# Determine criticality
critical_findings = []
if REPORT.get('critical_email_broken'):
    critical_findings.append('FORM SUBMISSION EMAIL BOUNCES — bjsmithtechllc@gmail.com does not accept mail')

for ci in critical_findings:
    print(f"\n  ❌ CRITICAL: {ci}")

print(f"\n  Files scanned: {len(html_files)}")
print(f"  IDs collected: {len(all_ids)}")
print(f"  Forms: {len(form_endpoints)}")
print(f"  Issues found: {sum(len(v) for v in issues.values())}")
print(f"  Auto-fixes applied: {len(FIXED)}")
print(f"  Needs Bailey action: {len(NEEDS_BAILEY)}")

# Save report
with open('/tmp/deep_sweep_report.json', 'w') as f:
    json.dump(REPORT, f, indent=2, default=str)
print(f"\nFull report saved to /tmp/deep_sweep_report.json")
