/* eslint-disable prettier/prettier */
/* eslint-disable no-undef */

// Ajax request to send to server with the information user put in 
function send_late_ajax(event_date, minutes_late, delete_current){
    $.ajax({
        data: {
            'date': event_date,
            'minutes_late': minutes_late,
            'delete': delete_current,
        },
        dataType: 'json',
    })
}

// Open and close Modal
let events_modal = $('#events-late-modal')
let events_modal_open_btn = $('.events_modal_open_btn')
let events_modal_close_btn = $('.close-btn')
let events_modal_submit_btn = $('.submit-btn')
let events_modal_delete_btn = $('.delete-btn')
let events_modal_header_date = $('#input-modal-header-date')
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

$(events_modal_delete_btn).click(function(){
    send_late_ajax(event_date, 0, delete_current='True')
    toggle_events_modal()
    status_alert(2000, "Late Time Removed: " + event_date, "warning")
})

$(events_modal_submit_btn).click(function(){
    let selected_value = $('#events-modal-mins-late-dropdown :selected').val()
    send_late_ajax(event_date, selected_value, delete_current='False')
    toggle_events_modal()
    status_alert(2000, "Late Time Saved: " +event_date +" " +selected_value, "success")
})


