$('.navbar-hamburger-close').click(function(){
    $('.navbar-hamburger-menu-content').removeClass('open');
    $('.navbar-hamburger-menu').removeClass('open');
});
$('.hamburger-menu-toggle-button').click(function(){
    $('.navbar-hamburger-menu-content').toggleClass('open');
    $('.navbar-hamburger-menu').toggleClass('open');
});

$(document).ready(function(){
    let navbar_buttons = $('.navbar-links .nav-item a')

    function strip_href_string(str){
        return str.split('/',2).join('/')
    }

    for(i = 0; i<navbar_buttons.length;i++){
        href = strip_href_string($(navbar_buttons[i]).attr('href'))
        window_location = strip_href_string(window.location.pathname)
        if(href == window_location){
            $(navbar_buttons[i]).addClass('active')
        }
    }
})



