1|// ColoringSubmission.com — Full App
2|document.addEventListener('DOMContentLoaded', () => {
3|  // Copyright year
4|  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
5|
6|  // Mobile nav toggle
7|  const navToggle = document.querySelector('.nav-toggle');
8|  const navLinks = document.querySelector('.nav-links');
9|  if (navToggle && navLinks) {
10|    navToggle.addEventListener('click', () => {
11|      navLinks.classList.toggle('open');
12|      navToggle.setAttribute('aria-expanded', navLinks.classList.contains('open'));
13|    });
14|  }
15|
16|  // Newsletter form — real FormSubmit integration
17|  document.querySelectorAll('[data-demo-form]').forEach(form => {
18|    if (form.classList.contains('newsletter')) {
19|      form.addEventListener('submit', async e => {
20|        e.preventDefault();
21|        const email = form.querySelector('input[type="email"]')?.value;
22|        const msg = form.querySelector('.form-message');
23|        if (email && msg) {
24|          try {
25|            const body = new URLSearchParams();
26|            body.append('_subject', 'ColoringSubmission newsletter signup');
27|            body.append('_captcha', 'false');
28|            body.append('email', email);
29|            body.append('_next', 'https://usetalos.com/thank-you/?type=newsletter');
30|            await fetch('https://formsubmit.co/talos.mnb@gmail.com', { method: 'POST', body });
31|            msg.textContent = form.dataset.success || 'Thanks! Check your email.';
32|            msg.style.color = '#9fbd74';
33|          } catch(e) {
34|            msg.textContent = 'Something went wrong. Please email us at talos.mnb@gmail.com.';
35|            msg.style.color = '#ffbe8a';
36|          }
37|          msg.classList.add('show');
38|          form.reset();
39|          setTimeout(() => msg.classList.remove('show'), 4000);
40|        }
41|      });
42|    } else {
43|      form.addEventListener('submit', e => {
44|        e.preventDefault();
45|        const msg = form.querySelector('.form-message');
46|        if (msg) {
47|          msg.textContent = form.dataset.success || 'Thanks! Your submission has been received.';
48|          msg.classList.add('show');
49|        }
50|        form.reset();
51|        setTimeout(() => msg?.classList.remove('show'), 4000);
52|      });
53|    }
54|  });
55|
56|  // Gallery filters
57|  const filterBtns = document.querySelectorAll('[data-filter]');
58|  const cards = document.querySelectorAll('[data-category]');
59|  filterBtns.forEach(btn => {
60|    btn.addEventListener('click', () => {
61|      const filter = btn.dataset.filter;
62|      filterBtns.forEach(b => b.classList.remove('active'));
63|      btn.classList.add('active');
64|      cards.forEach(card => {
65|        card.hidden = filter !== 'all' && card.dataset.category !== filter;
66|      });
67|    });
68|  });
69|
70|  // Age gate
71|  const gateForm = document.querySelector('#ageGateForm');
72|  const gateCard = document.querySelector('#ageGate');
73|  const adultStore = document.querySelector('#adultStore');
74|  const gateError = document.querySelector('#gateError');
75|
76|  if (sessionStorage.getItem('coloringAdultVerified') === 'true') {
77|    gateCard?.classList.add('hidden');
78|    adultStore?.classList.add('unlocked');
79|  }
80|
81|  gateForm?.addEventListener('submit', e => {
82|    e.preventDefault();
83|    const y = +document.querySelector('#birthYear')?.value;
84|    const m = +document.querySelector('#birthMonth')?.value;
85|    const d = +document.querySelector('#birthDay')?.value;
86|    const bd = new Date(y, m - 1, d);
87|    const valid = bd.getFullYear() === y && bd.getMonth() === m - 1 && bd.getDate() === d;
88|    let age = new Date().getFullYear() - y;
89|    if (new Date().getMonth() + 1 < m || (new Date().getMonth() + 1 === m && new Date().getDate() < d)) age--;
90|    
91|    if (valid && age >= 18) {
92|      sessionStorage.setItem('coloringAdultVerified', 'true');
93|      gateCard?.classList.add('hidden');
94|      adultStore?.classList.add('unlocked');
95|      gateError?.classList.remove('show');
96|      adultStore?.scrollIntoView({ behavior: 'smooth' });
97|    } else {
98|      gateError?.classList.add('show');
99|    }
100|  });
101|
102|  // Newsletter signup
103|  document.querySelectorAll('[data-newsletter]').forEach(form => {
104|    form.addEventListener('submit', e => {
105|      e.preventDefault();
106|      const email = form.querySelector('input[type="email"]')?.value;
107|      const msg = form.querySelector('.form-message');
108|      if (email && msg) {
109|        console.log('Newsletter signup:', email);
110|        msg.textContent = 'You\'re in! Check your email.';
111|        msg.classList.add('show');
112|        form.reset();
113|        setTimeout(() => msg.classList.remove('show'), 4000);
114|      }
115|    });
116|  });
117|
118|  // Smooth scroll for anchor links
119|  document.querySelectorAll('a[href^="#"]').forEach(link => {
120|    link.addEventListener('click', e => {
121|      const target = document.querySelector(link.getAttribute('href'));
122|      if (target) {
123|        e.preventDefault();
124|        target.scrollIntoView({ behavior: 'smooth' });
125|      }
126|    });
127|  });
128|
129|  // Lazy load images
130|  if ('IntersectionObserver' in window) {
131|    const observer = new IntersectionObserver((entries) => {
132|      entries.forEach(entry => {
133|        if (entry.isIntersecting) {
134|          const img = entry.target;
135|          if (img.dataset.src) {
136|            img.src = img.dataset.src;
137|            img.removeAttribute('data-src');
138|          }
139|          observer.unobserve(img);
140|        }
141|      });
142|    }, { rootMargin: '200px' });
143|    document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
144|  }
145|});
146|