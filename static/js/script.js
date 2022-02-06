$('.navbar-hamburger-close').click(function(){
    $('.navbar-hamburger-menu-content').removeClass('open');
    $('.navbar-hamburger-menu').removeClass('open');
});
$('.hamburger-menu-toggle-button').click(function(){
    $('.navbar-hamburger-menu-content').toggleClass('open');
    $('.navbar-hamburger-menu').toggleClass('open');
});
