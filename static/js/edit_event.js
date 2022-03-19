function delete_event(event_date){
    if(confirm("Delete Event: " + event_date+"?")){
        window.location.replace('/delete_event/'+event_date)
    }
}