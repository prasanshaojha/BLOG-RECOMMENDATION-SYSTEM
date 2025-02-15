$(document).ready(function () {
    // Toggle main menu visibility
    $('.menu-toggle').on('click', function () {
        $('.nav').toggleClass('showing');
  
        // Toggle the aria-expanded attribute
        const expanded = $(this).attr('aria-expanded') === 'true';
        $(this).attr('aria-expanded', !expanded);
    });
  
    // Submenu toggle for mobile
    $('.nav > li > a').on('click', function (e) {
        if ($(window).width() <= 768) { // Check if the screen is small
            const submenu = $(this).next('ul');
            if (submenu.length) {
                e.preventDefault(); // Prevent default link behavior if submenu exists
                submenu.toggleClass('showing');
            }
        }
    });
  
    // Slick slider initialization
    $('.multiple-items').slick({
        infinite: true,
        slidesToShow: 3,        // Display 3 items at a time
        slidesToScroll: 1,      // Scroll one item at a time
        nextArrow: $('.next'),
        prevArrow: $('.prev'),
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 1,
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
        ]
    });
    console.log('Slick initialized');
  });
  

