from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]

# 1) Create clean route aliases required by QA.
aliases = {
    'personal-ai': root / 'personal-ai.html',
    'get-help': root / 'consultation' / 'index.html',
    'consulting': root / 'consultation' / 'index.html',
}
for route, src in aliases.items():
    dest_dir = root / route
    dest_dir.mkdir(exist_ok=True)
    shutil.copyfile(src, dest_dir / 'index.html')

# 2) Ensure blog and any HTML missing the shared stylesheet gets it in head.
for html in root.glob('**/*.html'):
    if any(part in {'.git', 'node_modules', 'qa-artifacts', 'test-results'} for part in html.parts):
        continue
    s = html.read_text()
    if '/assets/styles.css' not in s:
        marker = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
        if marker in s:
            s = s.replace(marker, marker + '\n  <link rel="stylesheet" href="/assets/styles.css" />', 1)
            html.write_text(s)

# 3) Newsletter fallback: replace iframe-only block with branded native fallback + iframe.
newsletter = root / 'newsletter' / 'index.html'
s = newsletter.read_text()
old = '''        <div class="beehiiv-embed">
          <iframe src="https://embeds.beehiiv.com/pub_29a390aa-0b31-4acd-896a-c3efbeb77f87" 
                  data-test-id="beehiiv-embed" 
                  height="420" 
                  frameborder="0" 
                  scrolling="no" 
                  style="margin:0;border-radius:16px !important;background-color:transparent">
          </iframe>
        </div>'''
new = '''        <div class="newsletter-shell card" aria-label="Newsletter signup">
          <div class="newsletter-fallback">
            <span class="badge gold">Free weekly briefing</span>
            <h3>Newsletter signup is loading.</h3>
            <p>If it does not appear, email <a href="mailto:talos.mnb@gmail.com">talos.mnb@gmail.com</a>.</p>
            <form class="newsletter-native" action="https://formsubmit.co/talos.mnb@gmail.com" method="POST" accept-charset="UTF-8">
              <input type="hidden" name="_subject" value="Tal.OS newsletter signup" />
              <input type="hidden" name="_captcha" value="false" />
              <label for="newsletter-email">Email address</label>
              <input id="newsletter-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required />
              <button class="btn" type="submit">Join the Newsletter</button>
            </form>
          </div>
          <iframe class="beehiiv-frame" src="https://embeds.beehiiv.com/pub_29a390aa-0b31-4acd-896a-c3efbeb77f87" data-test-id="beehiiv-embed" title="Tal.OS newsletter signup" loading="lazy"></iframe>
        </div>'''
if old in s:
    s = s.replace(old, new, 1)
else:
    print('newsletter block not found; skipped iframe replacement')
newsletter.write_text(s)

# 4) Normalize old hrefs to clean routes.
for html in root.glob('**/*.html'):
    if any(part in {'.git', 'node_modules', 'qa-artifacts', 'test-results'} for part in html.parts):
        continue
    s = html.read_text()
    s = s.replace('/personal-ai.html', '/personal-ai/')
    html.write_text(s)

print('mobile QA structural fixes applied')
