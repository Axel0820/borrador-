/*Swiper*/ /*Carrusel de card*/
var swiperCategories = new Swiper('.categories__container',{
    spaceBetween: 24,
    loop: true,
    navigation:{
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    breakpoints:{
        1400:{
            slidesPerView: 7,
            spaceBetween: 20,
        },
        768:{
            slidesPerView: 5,
            spaceBetween:15,
        },
        640:{
            slidesPerView: 3,
            spaceBetween: 15,
        },
        420:{
            slidesPerView: 2,
            spaceBetween: 10,
        }   
    }
});
/*Swiper*/ /*Carrusel de card*/
