// ColoringSubmission.com — Full App
document.addEventListener('DOMContentLoaded', () => {
  // Copyright year
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());

  // Mobile nav toggle
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', navLinks.classList.contains('open'));
    });
  }

  // Demo forms
  document.querySelectorAll('[data-demo-form]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const msg = form.querySelector('.form-message');
      if (msg) {
        msg.textContent = form.dataset.success || 'Thanks! Your submission has been received.';
        msg.classList.add('show');
      }
      form.reset();
      setTimeout(() => msg?.classList.remove('show'), 4000);
    });
  });

  // Gallery filters
  const filterBtns = document.querySelectorAll('[data-filter]');
  const cards = document.querySelectorAll('[data-category]');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      cards.forEach(card => {
        card.hidden = filter !== 'all' && card.dataset.category !== filter;
      });
    });
  });

  // Age gate
  const gateForm = document.querySelector('#ageGateForm');
  const gateCard = document.querySelector('#ageGate');
  const adultStore = document.querySelector('#adultStore');
  const gateError = document.querySelector('#gateError');

  if (sessionStorage.getItem('coloringAdultVerified') === 'true') {
    gateCard?.classList.add('hidden');
    adultStore?.classList.add('unlocked');
  }

  gateForm?.addEventListener('submit', e => {
    e.preventDefault();
    const y = +document.querySelector('#birthYear')?.value;
    const m = +document.querySelector('#birthMonth')?.value;
    const d = +document.querySelector('#birthDay')?.value;
    const bd = new Date(y, m - 1, d);
    const valid = bd.getFullYear() === y && bd.getMonth() === m - 1 && bd.getDate() === d;
    let age = new Date().getFullYear() - y;
    if (new Date().getMonth() + 1 < m || (new Date().getMonth() + 1 === m && new Date().getDate() < d)) age--;
    
    if (valid && age >= 18) {
      sessionStorage.setItem('coloringAdultVerified', 'true');
      gateCard?.classList.add('hidden');
      adultStore?.classList.add('unlocked');
      gateError?.classList.remove('show');
      adultStore?.scrollIntoView({ behavior: 'smooth' });
    } else {
      gateError?.classList.add('show');
    }
  });

  // Newsletter signup
  document.querySelectorAll('[data-newsletter]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const email = form.querySelector('input[type="email"]')?.value;
      const msg = form.querySelector('.form-message');
      if (email && msg) {
        console.log('Newsletter signup:', email);
        msg.textContent = 'You\'re in! Check your email.';
        msg.classList.add('show');
        form.reset();
        setTimeout(() => msg.classList.remove('show'), 4000);
      }
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Lazy load images
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });
    document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
  }
});
