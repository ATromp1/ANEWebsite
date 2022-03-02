function status_alert(time_to_display, text, status_type){
    status_type = status_type || "info"
    e = $('.status-alert')
    $(e).toggleClass('active ' + status_type)
    $(e).first().text(text)
    setTimeout(function(){
        $(e).toggleClass('active ' + status_type)
    }, time_to_display)
}

function unslugify_string(slug) {
    const result = slug.replace(/\_/g, " ");
    return result.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

$(document).ready(function(){
    /*
    Highlight the current button on navbar depending on page
    */
    function strip_href_string(str){
        return str.split('/',2).join('/')
    }
    let navbar_buttons = $('.navbar-links .nav-item a')
    for(i = 0; i<navbar_buttons.length;i++){
        href = strip_href_string($(navbar_buttons[i]).attr('href'))
        window_location = strip_href_string(window.location.pathname)
        if(href == window_location){
            $(navbar_buttons[i]).addClass('active')
        }
    }
})

$('.navbar-hamburger-close').click(function(){
    $('.navbar-hamburger-menu-content').removeClass('open');
    $('.navbar-hamburger-menu').removeClass('open');
});
$('.hamburger-menu-toggle-button').click(function(){
    $('.navbar-hamburger-menu-content').toggleClass('open');
    $('.navbar-hamburger-menu').toggleClass('open');
});
//$('.hamburger-menu-toggle-button').click(function(){
//    $('.navbar-hamburger-menu-content').addClass('open');
//    $('.navbar-hamburger-menu').addClass('open');
//});
