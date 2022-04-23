function status_alert(time_to_display, text, status_type){
    status_type = status_type || "info"
    e = $('.status-alert')
    setTimeout(() => {
        $(e).addClass('active ' + status_type)
        $(e).first().text(text)
    },200)
    setTimeout(() => {
        $(e).removeClass('active ' + status_type)
    }, time_to_display)
}

function unslugify_string(slug) {
    const result = slug.replace(/\_/g, " ");
    return result.replace(/\w\S*/g, function (txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}
function strip_href_string(str){
    return str.split('/',2).join('/')
}
function resetLastVisitedBossView(){
    sessionStorage.setItem('lastVisitedBossView', null)
}
if(strip_href_string(window.location.pathname) != "/events"){
    resetLastVisitedBossView()
}

$(document).ready(function(){
    /*
    Highlight the current button on navbar depending on page
    */
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

if(strip_href_string(window.location.pathname) == "/events"){
    console.log("Preloaded Boss Images not in Cache")
    var images = [];
    function preload() {
        for (var i = 0; i < arguments.length; i++) {
            images[i] = new Image();
            images[i].src = preload.arguments[i];
        }
    }
    preload(
        "/static/images/bossImages/Sepulcher/VigilantGuardianBG.jpg",
        "/static/images/bossImages/Sepulcher/SkolexBG.jpg",
        "/static/images/bossImages/Sepulcher/ArtificerXyMoxBG.jpg",
        "/static/images/bossImages/Sepulcher/DausegneBG.jpg",
        "/static/images/bossImages/Sepulcher/PrototypePantheonBG.jpg",
        "/static/images/bossImages/Sepulcher/LihuvimBG.jpg",
        "/static/images/bossImages/Sepulcher/HalondrusBG.jpg",
        "/static/images/bossImages/Sepulcher/AnduinWrynnBG.jpg",
        "/static/images/bossImages/Sepulcher/LordsOfDreadBG.jpg",
        "/static/images/bossImages/Sepulcher/RygelonBG.jpg",
        "/static/images/bossImages/Sepulcher/TheJailerBG.jpg"
    )
}


// Enable Bootstrap Tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

function getQuerySetFields(querySet){
    let res = []
    querySet.forEach(e => {
        res.push(e.fields)
    });
    return res
}

function clamp(number, min, max) {
    return Math.max(min, Math.min(number, max));
}

function loadingButton(btn, statusText="", statusType="info", func) {
    const borderThickness = 2;
    btn.addClass('ane-btn-disabled')
    btn.attr('loading',true)
    let xPadding = (parseInt($(btn).css('padding-left') || 0) + parseInt($(btn).css('padding-right') || 0) + (borderThickness * 2)) / 2
    let yPadding = (parseInt($(btn).css('padding-top')  || 0) + parseInt($(btn).css('padding-bottom')|| 0) + (borderThickness * 2)) / 2
    console.log(xPadding)
    console.log(yPadding)
    $(btn).css('padding-left', xPadding);
    $(btn).css('padding-right', xPadding);
    $(btn).css('padding-bottom', yPadding);
    $(btn).css('padding-top', yPadding);
    setTimeout(()=>{
        btn.removeAttr('loading')
        btn.removeAttr('style')
        if(statusText != "")
            status_alert(1500, statusText, statusType)
        if(func)
            func()
    },(Math.random()+0.1)*1000*1.5)

}