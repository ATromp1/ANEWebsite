// Ajax request to send to server with the information user put in 
function send_late_ajax(event_date, minutes_late, delete_current){
    $.ajax({
        data: {
            'type': 'late',
            'date': event_date,
            'minutes_late': minutes_late,
            'delete': delete_current,
        },
        dataType: 'json',
    })
}

function update_raid_status_ajax(event_date, request_type){
    $.ajax({
        data:{
            'type':request_type,
            'date':event_date,
        },
        dataType: 'json',
    })

}
function attend_raid(e){
    let event_date = e.id
    update_raid_status_ajax(event_date, "attend")
    status_alert(2000, "You are no longer marked as absent for raid: " + event_date, "success")
    update_event_display(e)
}
function confirm_decline_raid(e){
    let event_date = e.id
    let res = confirm("Decline raid: " + event_date + "?")
    if(res){
        update_raid_status_ajax(event_date, "decline")
        status_alert(2000,"Declined raid: " + event_date, "warning")
        update_event_display(e)
    } else{
        return
    }
}
function update_event_display(element){
    let absent_div = $('#'+element.id+'.event-list-user-options.absent')
    let present_div = $('#'+element.id+'.event-list-user-options.present')
    let date_div = $('#'+element.id+'.event-list-date')
    date_div.toggleClass("selected absent")
    absent_div.toggleClass('disabled')
    present_div.toggleClass('disabled')
}

$('.event-view-attendance-btn').click(function(){
    setTimeout(function(){
        window.location.reload()
    },100)
})

// Open and close Modal
const events_modal = $('#events-late-modal')
const events_modal_open_btn = $('.events_modal_open_btn')
const events_modal_close_btn = $('#late-modal-close')
const events_modal_submit_btn = $('#late-modal-submit')
const events_modal_delete_btn = $('#late-modal-delete')
const events_modal_header_date = $('#input-modal-header-date')
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


