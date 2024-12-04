document.querySelectorAll('.nav-button').forEach(button => {
    button.addEventListener('click', event => {
      event.preventDefault();
      const href = event.target.getAttribute('href');
      document.body.style.opacity = '0';
      setTimeout(() => {
        window.location.href = href;
      }, 300);
    });
  });
  window.onload = () => {
    document.body.style.transition = 'opacity 0.3s';
    document.body.style.opacity = '1';
  };