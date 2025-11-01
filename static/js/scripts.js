// basic interactivity: counters, scroll reveal, feedback AJAX
document.addEventListener('DOMContentLoaded', () => {
  // Simple counters (demo)
  const counters = [
    { id: 'cnt-users', end: 500 },
    { id: 'cnt-drivers', end: 40 },
    { id: 'cnt-rides', end: 3000 }
  ];
  counters.forEach(c => {
    const el = document.getElementById(c.id);
    if (!el) return;
    let cur = 0;
    const step = Math.max(1, Math.floor(c.end / 60));
    const t = setInterval(() => {
      cur += step;
      if (cur >= c.end) { cur = c.end; clearInterval(t); }
      el.textContent = cur + (c.end > 100 ? '+' : '');
    }, 18);
  });

  // scroll reveal - using AOS on page, but also simple fallback
  window.addEventListener('scroll', () => {
    document.querySelectorAll('.panel').forEach(p => {
      const top = p.getBoundingClientRect().top;
      if (top < window.innerHeight - 80) p.classList.add('visible');
    });
  });

  // Feedback form AJAX submit (if used)
  const fbForm = document.querySelector('#feedbackForm');
  if (fbForm) {
    fbForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new URLSearchParams(new FormData(fbForm));
      try {
        const res = await fetch('/feedback', { method: 'POST', body: formData });
        const j = await res.json();
        if (j.status === 'success') {
          alert('Thanks — feedback received!');
          fbForm.reset();
        } else {
          alert('There was an error.');
        }
      } catch (err) { alert('Network error.'); }
    });
  }
});


