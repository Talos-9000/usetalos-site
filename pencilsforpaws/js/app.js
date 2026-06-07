1|document.addEventListener('DOMContentLoaded',()=>{
2|  document.querySelectorAll('[data-year]').forEach(el=>el.textContent=new Date().getFullYear());
3|  const toggle=document.querySelector('.nav-toggle');
4|  const nav=document.querySelector('.nav-links');
5|  if(toggle&&nav){
6|    toggle.addEventListener('click',()=>{
7|      const open=nav.classList.toggle('open');
8|      toggle.setAttribute('aria-expanded',open?'true':'false');
9|    });
10|    nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')))
11|  }
12|  document.querySelectorAll('a[href^="#"]').forEach(link=>{
13|    link.addEventListener('click',e=>{
14|      const target=document.querySelector(link.getAttribute('href'));
15|      if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth',block:'start'})}
16|    })
17|  });
18|  document.querySelectorAll('[data-filter]').forEach(btn=>{
19|    btn.addEventListener('click',()=>{
20|      const f=btn.dataset.filter;
21|      document.querySelectorAll('[data-filter]').forEach(b=>b.classList.remove('active'));
22|      btn.classList.add('active');
23|      document.querySelectorAll('[data-animal]').forEach(card=>{card.hidden=f!=='all'&&card.dataset.animal!==f})
24|    })
25|  });
26|  // Real form submissions via FormSubmit
27|  document.querySelectorAll('form').forEach(form=>{
28|    form.addEventListener('submit',async function(e){
29|      if(form.hasAttribute('data-demo-form')||form.id==='petSubmissionForm'||form.hasAttribute('data-newsletter')){
30|        e.preventDefault();
31|        let ok=true;
32|        form.querySelectorAll('[required]').forEach(field=>{
33|          if((field.type==='checkbox'&&!field.checked)||!field.value){ok=false;field.setAttribute('aria-invalid','true')}
34|          else{field.removeAttribute('aria-invalid')}
35|        });
36|        const emailField=form.querySelector('input[type="email"]');
37|        if(emailField&&emailField.value&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)){ok=false;emailField.setAttribute('aria-invalid','true')}
38|        if(!ok){
39|          const msg=form.querySelector('.form-message');
40|          if(msg){msg.textContent='Please complete the required fields before submitting.';msg.classList.add('show');msg.style.color='#ffbe8a';setTimeout(()=>msg.classList.remove('show'),4000)}
41|          return;
42|        }
43|        // Submit to FormSubmit
44|        const msg=form.querySelector('.form-message');
45|        try{
46|          const body=new URLSearchParams();
47|          body.append('_subject','Pencils for Paws submission');
48|          body.append('_captcha','false');
49|          body.append('_next','https://usetalos.com/thank-you/?type=consultation');
50|          new FormData(form).forEach((v,k)=>body.append(k,v));
51|          await fetch('https://formsubmit.co/talos.mnb@gmail.com',{method:'POST',body});
52|          if(msg){msg.textContent=form.dataset.success||'Thanks! We received your request.';msg.classList.add('show');msg.style.color='#9fbd74'}
53|          form.reset();
54|        }catch(e){
55|          if(msg){msg.textContent='Something went wrong. Please email us at talos.mnb@gmail.com.';msg.classList.add('show');msg.style.color='#ffbe8a'}
56|        }
57|        setTimeout(()=>msg&&msg.classList.remove('show'),4000);
58|      }
59|    })
60|  })
61|})