
    $(document).ready(function () {
    $('.multiple-items').slick({
        slidesToShow: 3,
        slidesToScroll: 1,
        arrows: true, // Keep arrows enabled
        prevArrow: $('.prev'),
        nextArrow: $('.next'),
        autoplay: true, // Enable automatic sliding
        autoplaySpeed: 3000, // Slide every 3 seconds
        responsive: [
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
        ]
    });

    // Hide arrows initially
    $('.prev, .next').hide();

    let fadeOutTimeout;

    // Show arrows on hover
    $('.multiple-items').hover(
        function () {
            clearTimeout(fadeOutTimeout); // Clear any existing timeout
            $('.prev, .next').fadeIn(); // Show arrows on hover
        },
        function () {
            fadeOutTimeout = setTimeout(function () {
                $('.prev, .next').fadeOut(); // Hide arrows after 2 seconds
            }, 2000); // 2000ms = 2 seconds
        }
    );
});
    
    window.addEventListener('scroll', function() {
  const posts = document.querySelectorAll('.fadeup');
  posts.forEach(post => {
    const rect = post.getBoundingClientRect();
    if (rect.top <= window.innerHeight) {
      post.classList.add('active');
    }
  });
});

