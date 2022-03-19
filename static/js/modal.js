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

const lateModal = (()=> {
    const modal = $('#events-late-modal')
    const openModalButton = $('.events_modal_open_btn')
    const closeModalButton = $('#late-modal-close')
    const submitModal = $('#late-modal-submit')
    const deleteSelectedValueButton = $('#late-modal-delete')
    let eventDate;

    $(openModalButton).click((e)=>{
        lateModal.openModal(e)
    })
    $(closeModalButton).click((e)=>{
        lateModal.closeModal(e)
    })
    $(submitModal).click((e)=>{
        submitForm(eventDate)
    })
    $(deleteSelectedValueButton).click((e)=>{
        deleteSelectedValue(eventDate)
    })

    function openModal(e){
        displayDate(e)
        $(modal).addClass('open')
    }
    function closeModal(e){
        $(modal).removeClass('open')
    }

    function displayDate(e){
        eventDate = e?.currentTarget.id || undefined
        $('#input-modal-header-date').text(eventDate)
    }

    function submitForm(eventDate){
        const selectedValue = $('#events-modal-mins-late-dropdown :selected').val()
        if(eventDate) { 
            send_late_ajax(eventDate, selectedValue, deleteCurrent='False')
            status_alert(2000, "Late Time Saved: " +eventDate +" " +selectedValue, "success")
            lateModal.closeModal()
        } else {
            status_alert(2000, "Error Saving", "danger")
        }
    }

    function deleteSelectedValue(eventDate){
        if(eventDate){
            send_late_ajax(eventDate, 0, delete_current='True')
            status_alert(2000, "Late Time Removed: " + eventDate, "warning")
            lateModal.closeModal()
        } else {
            status_alert(2000, "Error Removing Time", "danger")
        }
    }

    return {
        openModal: openModal,
        closeModal: closeModal,
    }
})();
