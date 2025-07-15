fetch("{% url 'api_recherche' %}", {
    method: 'POST',
    headers: {"X-CSRFToken": csrftoken},
    body: formData
})

'use strict';

// Récupère les éléments globaux
const header         = document.querySelector('header');
const nav            = document.querySelector('nav');
const menuBtn        = document.querySelector('.navbar-menu-btn');
const navContainer   = document.querySelector('.navbar-nav-container');
const searchBtn      = document.querySelector('.navbar-search-btn');
const searchForm     = document.querySelector('.navbar-form');
const searchCloseBtn = document.querySelector('.navbar-form-close');

document.addEventListener('DOMContentLoaded', () => {

  // 1) Toggle menu mobile
  if (menuBtn && navContainer) {
    menuBtn.addEventListener('click', () => {
      navContainer.classList.toggle('show');
      menuBtn.classList.toggle('open');
    });
  }

  // 2) Toggle recherche vocale
  if (searchBtn && searchForm) {
    searchBtn.addEventListener('click', () =>
      searchForm.classList.toggle('active')
    );
  }
  if (searchCloseBtn && searchForm) {
    searchCloseBtn.addEventListener('click', () =>
      searchForm.classList.remove('active')
    );
  }

  // 3) Drag & scroll pour le carousel
  const carousel = document.querySelector('.carousel-container');
  if (carousel) {
    let isDown = false,
        startX = 0,
        scrollLeft = 0;

    carousel.addEventListener('mousedown', e => {
      isDown = true;
      carousel.classList.add('active');
      startX = e.pageX - carousel.offsetLeft;
      scrollLeft = carousel.scrollLeft;
    });
    carousel.addEventListener('mouseleave', () => {
      isDown = false;
      carousel.classList.remove('active');
    });
    carousel.addEventListener('mouseup', () => {
      isDown = false;
      carousel.classList.remove('active');
    });
    carousel.addEventListener('mousemove', e => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - carousel.offsetLeft;
      const walk = (x - startX) * 2; // vitesse de scroll
      carousel.scrollLeft = scrollLeft - walk;
    });

    // Support tactile
    carousel.addEventListener('touchstart', e => {
      isDown = true;
      startX = e.touches[0].pageX - carousel.offsetLeft;
      scrollLeft = carousel.scrollLeft;
    });
    carousel.addEventListener('touchend', () => isDown = false);
    carousel.addEventListener('touchmove', e => {
      if (!isDown) return;
      const x = e.touches[0].pageX - carousel.offsetLeft;
      const walk = (x - startX) * 2;
      carousel.scrollLeft = scrollLeft - walk;
    });

    // 4) Défilement automatique infini
    const speed = 0.5; // pixels par frame
    let rafId;

    function autoScroll() {
      carousel.scrollLeft += speed;
      // si fin atteinte, remettre au début
      if (carousel.scrollLeft >= carousel.scrollWidth - carousel.clientWidth) {
        carousel.scrollLeft = 0;
      }
      rafId = requestAnimationFrame(autoScroll);
    }

    // démarre l'auto-scroll
    rafId = requestAnimationFrame(autoScroll);

    // pause au survol
    carousel.addEventListener('mouseenter', () => cancelAnimationFrame(rafId));
    carousel.addEventListener('mouseleave', () => rafId = requestAnimationFrame(autoScroll));
  }

});

// 5) Toggle header & nav (en dehors de DOMContentLoaded pour le menu burger)
if (menuBtn) {
  menuBtn.addEventListener('click', () => {
    header.classList.toggle('active');
    nav.classList.toggle('active');
    menuBtn.classList.toggle('active');
  });
}
// après avoir créé `const player = new Audio(url);`
const playBtn = document.getElementById('play-tts');
playBtn.addEventListener('click', () => player.play());
