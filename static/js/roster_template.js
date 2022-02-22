/* /.................// Roster Templates //................./ */

// Template save button
$('.event-view-save-template').click(function(){
    if(raid_event.currently_selected_boss_roster == -1){
        status_alert(2000, "Needs a Selected Boss", "warning")
        return
    }
    let template_name = prompt("Name of Template: ")
    save_roster_template(template_name)
})

// Open template modal
$('.event-view-load-template').click(function(){
    if(raid_event.currently_selected_boss_roster == -1){
        status_alert(2000, "Needs a Selected Boss", "warning")
        return
    }
    toggle_template_load_modal()
})

// Close template modal
$('#template-modal-close').click(function(){toggle_template_load_modal()})

// Load a template from modal
$('#template-modal-load').click(function(){
    let selected_value = $('#event-view-template-modal-dropdown :selected').val()
    toggle_template_load_modal()
    load_roster_template(selected_value)
})

// Delete a template from modal
$('#template-modal-delete').click(function(){
    let selected_value = $('#event-view-template-modal-dropdown :selected').val()
    let confirm_delete = confirm("Remove Template: " + selected_value+"?")
    if(confirm_delete){
        delete_roster_template(selected_value)
    }
})

function toggle_template_load_modal(){
    fill_template_modal_dropdown()
    $('#event-view-template-modal').toggleClass('open')
}

function fill_template_modal_dropdown(){
    let available_templates = get_available_templates()
    let dropdown_element = $('#event-view-template-modal-dropdown')
    $(dropdown_element).empty()
    jQuery.each(available_templates, function(){
        $('<option/>', {
            'value': this,
            'text': this
        }).appendTo(dropdown_element);
    });
    
}
/* Saves the roster for the currently selected boss */
function save_roster_template(template_name){
    if(typeof(Storage) !== "undefined"){
        // Quick name validation, must be between 1 and 25 chars
        if(template_name == null){return}
        if(template_name.length<1 || template_name.length>25){
            status_alert(2000, "Cannot Save: Invalid Name", "warning")
            return
        }

        let boss_id = raid_event.currently_selected_boss_roster
        let roster_to_save = raid_event.roster_per_boss_objects[boss_id].selected_roster
        // Check if roster contains characters
        if(roster_to_save.length<1){
            status_alert(2000, "Cannot Save: Roster is Empty", "danger")
            return
        }
        let jsonified_roster = JSON.stringify(roster_to_save)
        localStorage.setItem(template_name, jsonified_roster)


        let saved_roster_template_list = get_available_templates()
        saved_roster_template_list.push(template_name)
        let jsonified_list = JSON.stringify(saved_roster_template_list)
        localStorage.setItem("saved_roster_template_list", jsonified_list)

        status_alert(2000, "Template Saved As: " + template_name, "success")
    } else{
        status_alert(2000, "You don't have LocalStorage on your browser", "danger")
    }
}

function get_available_templates(){
    return JSON.parse(localStorage.getItem("saved_roster_template_list")) || []
}

function load_roster_template(template_name){
    let roster_from_localstorage = localStorage.getItem(template_name)
    let parsed_roster = JSON.parse(roster_from_localstorage)

    let boss_id = raid_event.currently_selected_boss_roster
    raid_event.roster_per_boss_objects[boss_id].load_roster_from_roster_list(parsed_roster)
    raid_event.roster_per_boss_objects[boss_id].display_selected_roster()
    raid_event.roster_per_boss_objects[boss_id].display_benched_roster()
    raid_event.roster_per_boss_objects[boss_id].display_buff_info()

    $.ajax({
        url: window.location.href,
        data: {
            'saved_setup': roster_from_localstorage,
            'boss_id': boss_id,
        },
        dataType: 'json',
        contentType: "application/json",
        success: status_alert(2000, "Template Loaded: " + template_name, "success"),
    })
} 

function delete_roster_template(template_name){
    // Overwrite existing storage containing our templates
    available_templates = get_available_templates()
    let item_index = available_templates.indexOf(template_name) 
    available_templates.splice(item_index, 1)
    localStorage.setItem("saved_roster_template_list", JSON.stringify(available_templates))

    localStorage.removeItem(template_name)
    fill_template_modal_dropdown()

    status_alert(2000, "Template deleted", "success")
}