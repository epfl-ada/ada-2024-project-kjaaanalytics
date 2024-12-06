window.transitionToPage = function(href) {
  document.querySelector('body').style.opacity = 0
  setTimeout(function() { 
      window.location.href = href       
  }, 300)
}

window.onload = () => {
  document.body.style.transition = 'opacity 0.3s';
  document.body.style.opacity = '1';  
};