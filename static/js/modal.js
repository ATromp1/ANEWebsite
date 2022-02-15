/* eslint-disable prettier/prettier */
/* eslint-disable no-undef */

// Ajax request to send to server with the information user put in 
function send_late_ajax(event_date, minutes_late){
    $.ajax({
        data: {
            'date': event_date,
            'minutes_late': minutes_late,
        },
        dataType: 'json',
    })
}

// Open and close Modal
let events_modal = $('.events-late-modal')
let events_modal_open_btn = $('.events_modal_open_btn')
let events_modal_close_btn = $('.close-btn')
let events_modal_submit_btn = $('.submit-btn')
let events_modal_header_date = $('#events-modal-header-date')
let event_date;
function toggle_events_modal(){
    $(events_modal).toggleClass('open')
}

$(events_modal_open_btn).click(function(){
    event_date = this.id
    $(events_modal_header_date).text(event_date)
    toggle_events_modal()
})

$(events_modal_close_btn).click(function(){
    toggle_events_modal()
})

$(events_modal_submit_btn).click(function(){
    let selected_value = $('#events-modal-mins-late-dropdown :selected').val()
    send_late_ajax(event_date, selected_value)
    toggle_events_modal()
    time_saved_alert(2000)
})

function time_saved_alert(time_to_display){
    e = $('.late-status-alert')
    $(e).toggleClass('active')

    setTimeout(function(){
        $(e).toggleClass('active')
    }, time_to_display)
}
