



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
let event_date;
function toggle_events_modal(){
    $(events_modal).toggleClass('open')
}

$(events_modal_open_btn).click(function(){
    event_date = this.id
    toggle_events_modal()
})

$(events_modal_close_btn).click(function(){
    toggle_events_modal()
})

$(events_modal_submit_btn).click(function(){
    let selected_value = $('#events-modal-mins-late-dropdown :selected').val()
    console.log(selected_value)
    console.log(event_date)
    send_late_ajax(event_date, selected_value)

    
})

