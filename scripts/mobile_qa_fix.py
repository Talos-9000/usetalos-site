1|from pathlib import Path
2|import shutil
3|
4|root = Path(__file__).resolve().parents[1]
5|
6|# 1) Create clean route aliases required by QA.
7|aliases = {
8|    'personal-ai': root / 'personal-ai.html',
9|    'get-help': root / 'consultation' / 'index.html',
10|    'consulting': root / 'consultation' / 'index.html',
11|}
12|for route, src in aliases.items():
13|    dest_dir = root / route
14|    dest_dir.mkdir(exist_ok=True)
15|    shutil.copyfile(src, dest_dir / 'index.html')
16|
17|# 2) Ensure blog and any HTML missing the shared stylesheet gets it in head.
18|for html in root.glob('**/*.html'):
19|    if any(part in {'.git', 'node_modules', 'qa-artifacts', 'test-results'} for part in html.parts):
20|        continue
21|    s = html.read_text()
22|    if '/assets/styles.css' not in s:
23|        marker = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
24|        if marker in s:
25|            s = s.replace(marker, marker + '\n  <link rel="stylesheet" href="/assets/styles.css" />', 1)
26|            html.write_text(s)
27|
28|# 3) Newsletter fallback: replace iframe-only block with branded native fallback + iframe.
29|newsletter = root / 'newsletter' / 'index.html'
30|s = newsletter.read_text()
31|old = '''        <div class="beehiiv-embed">
32|          <iframe src="https://embeds.beehiiv.com/pub_29a390aa-0b31-4acd-896a-c3efbeb77f87" 
33|                  data-test-id="beehiiv-embed" 
34|                  height="420" 
35|                  frameborder="0" 
36|                  scrolling="no" 
37|                  style="margin:0;border-radius:16px !important;background-color:transparent">
38|          </iframe>
39|        </div>'''
40|new = '''        <div class="newsletter-shell card" aria-label="Newsletter signup">
41|          <div class="newsletter-fallback">
42|            <span class="badge gold">Free weekly briefing</span>
43|            <h3>Newsletter signup is loading.</h3>
44|            <p>If it does not appear, email <a href="mailto:talos.mnb@gmail.com">talos.mnb@gmail.com</a>.</p>
45|            <form class="newsletter-native" action="https://formsubmit.co/talos.mnb@gmail.com" method="POST" accept-charset="UTF-8">
46|              <input type="hidden" name="_subject" value="Tal.OS newsletter signup" />
47|              <input type="hidden" name="_captcha" value="false" />
48|              <label for="newsletter-email">Email address</label>
49|              <input id="newsletter-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required />
50|              <button class="btn" type="submit">Join the Newsletter</button>
51|            </form>
52|          </div>
53|          <iframe class="beehiiv-frame" src="https://embeds.beehiiv.com/pub_29a390aa-0b31-4acd-896a-c3efbeb77f87" data-test-id="beehiiv-embed" title="Tal.OS newsletter signup" loading="lazy"></iframe>
54|        </div>'''
55|if old in s:
56|    s = s.replace(old, new, 1)
57|else:
58|    print('newsletter block not found; skipped iframe replacement')
59|newsletter.write_text(s)
60|
61|# 4) Normalize old hrefs to clean routes.
62|for html in root.glob('**/*.html'):
63|    if any(part in {'.git', 'node_modules', 'qa-artifacts', 'test-results'} for part in html.parts):
64|        continue
65|    s = html.read_text()
66|    s = s.replace('/personal-ai.html', '/personal-ai/')
67|    html.write_text(s)
68|
69|print('mobile QA structural fixes applied')
70|