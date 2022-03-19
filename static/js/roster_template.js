/* /.................// Roster Templates //................./ */
const templateModal = (()=> {
    const modal = $('#event-view-template-modal')
    const openModalButton = $('.event-view-load-template')
    const closeModalButton = $('#template-modal-close')
    const submitModal = $('#template-modal-load')
    const deleteSelectedValueButton = $('#template-modal-delete')
    let eventDate;

    $(openModalButton).click(()=>{
        templateModal.openModal()
    })
    $(closeModalButton).click(()=>{
        templateModal.closeModal()
    })
    $(submitModal).click((e)=>{
        submitForm(eventDate)
    })
    $(deleteSelectedValueButton).click((e)=>{
        deleteSelectedValue(eventDate)
    })

    function openModal(){
        fillTemplateModalDropdown()
        $(modal).addClass('open')
    }
    function closeModal(){
        $(modal).removeClass('open')
    }

    function fillTemplateModalDropdown(){
        const availableTemplates = get_available_templates()
        const dropdownElement = $('#event-view-template-modal-dropdown')
        $(dropdownElement).empty()
        jQuery.each(availableTemplates, function(){
            $('<option/>', {
                'value': this,
                'text': this
            }).appendTo(dropdownElement);
        });
    }

    function submitForm(){
        const selectedValue = $('#events-modal-mins-late-dropdown :selected').val()

    }

    function deleteTemplate(templateName){
        // Overwrite existing storage containing our templates
        availableTemplates = get_available_templates()
        let itemIndex = availableTemplates.indexOf(templateName) 
        availableTemplates.splice(itemIndex, 1)
        localStorage.setItem("saved_roster_template_list", JSON.stringify(availableTemplates))
        localStorage.removeItem(templateName)

        fillTemplateModalDropdown()
        status_alert(2000, "Template deleted", "success")
    }

    function deleteSelectedValue(){
        const templateName = $('#event-view-template-modal-dropdown :selected').val()
        if(templateName){ 
            let confirmDelete = confirm("Remove Template: " + templateName+"?")
            if(confirmDelete){
                deleteTemplate(templateName)
            }
        } else {
            status_alert(2000, "No such template exists", "warning")
        }
    }

    return {
        openModal: openModal,
        closeModal: closeModal,
        fillTemplateModalDropdown: fillTemplateModalDropdown,
    }
})();

// Template save button
$('.event-view-save-template').click(function(){
    if(raid_event.currently_selected_boss_roster == -1){
        status_alert(2000, "Needs a Selected Boss", "warning")
        return
    }
    let template_name = prompt("Name of Template: ")
    save_roster_template(template_name)
})

// Load a template from modal
$('#template-modal-load').click(function(){
    let selected_value = $('#event-view-template-modal-dropdown :selected').val()
    templateModal.closeModal()
    if(selected_value){
         load_roster_template(selected_value)
    } else {
        status_alert(2000, "No such template exists", "warning")
    }
})

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