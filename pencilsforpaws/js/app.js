document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-year]').forEach(el=>el.textContent=new Date().getFullYear());
  const toggle=document.querySelector('.nav-toggle');
  const nav=document.querySelector('.nav-links');
  if(toggle&&nav){
    toggle.addEventListener('click',()=>{
      const open=nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded',open?'true':'false');
    });
    nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')))
  }
  document.querySelectorAll('a[href^="#"]').forEach(link=>{
    link.addEventListener('click',e=>{
      const target=document.querySelector(link.getAttribute('href'));
      if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth',block:'start'})}
    })
  });
  document.querySelectorAll('[data-filter]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const f=btn.dataset.filter;
      document.querySelectorAll('[data-filter]').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('[data-animal]').forEach(card=>{card.hidden=f!=='all'&&card.dataset.animal!==f})
    })
  });
  // Real form submissions via FormSubmit
  document.querySelectorAll('form').forEach(form=>{
    form.addEventListener('submit',async function(e){
      if(form.hasAttribute('data-demo-form')||form.id==='petSubmissionForm'||form.hasAttribute('data-newsletter')){
        e.preventDefault();
        let ok=true;
        form.querySelectorAll('[required]').forEach(field=>{
          if((field.type==='checkbox'&&!field.checked)||!field.value){ok=false;field.setAttribute('aria-invalid','true')}
          else{field.removeAttribute('aria-invalid')}
        });
        const emailField=form.querySelector('input[type="email"]');
        if(emailField&&emailField.value&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)){ok=false;emailField.setAttribute('aria-invalid','true')}
        if(!ok){
          const msg=form.querySelector('.form-message');
          if(msg){msg.textContent='Please complete the required fields before submitting.';msg.classList.add('show');msg.style.color='#ffbe8a';setTimeout(()=>msg.classList.remove('show'),4000)}
          return;
        }
        // Submit to FormSubmit
        const msg=form.querySelector('.form-message');
        try{
          const body=new URLSearchParams();
          body.append('_subject','Pencils for Paws submission');
          body.append('_captcha','true');
          body.append('_next','https://usetalos.com/thank-you/?type=consultation');
          new FormData(form).forEach((v,k)=>body.append(k,v));
          await fetch('https://formsubmit.co/talos.mnb@gmail.com',{method:'POST',body});
          if(msg){msg.textContent=form.dataset.success||'Thanks! We received your request.';msg.classList.add('show');msg.style.color='#9fbd74'}
          form.reset();
        }catch(e){
          if(msg){msg.textContent='Something went wrong. Please email us at talos.mnb@gmail.com.';msg.classList.add('show');msg.style.color='#ffbe8a'}
        }
        setTimeout(()=>msg&&msg.classList.remove('show'),4000);
      }
    })
  })
})