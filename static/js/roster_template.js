/* /.................// Roster Templates //................./ */
const templateModal = (() => {
    const modal = $('#event-view-template-modal')
    const openModalButton = $('.event-view-load-template')
    const closeModalButton = $('#template-modal-close')
    const submitModal = $('#template-modal-load')
    const deleteSelectedValueButton = $('#template-modal-delete')
    let eventDate;

    $(openModalButton).click(() => {
        templateModal.openModal()
    })
    $(closeModalButton).click(() => {
        templateModal.closeModal()
    })
    $(submitModal).click((e) => {
        submitForm(eventDate)
    })
    $(deleteSelectedValueButton).click((e) => {
        deleteSelectedValue(eventDate)
    })

    function openModal() {
        fillTemplateModalDropdown()
        $(modal).addClass('open')
    }

    function closeModal() {
        $(modal).removeClass('open')
    }

    function fillTemplateModalDropdown() {
        const availableTemplates = $templates.available_templates
        const dropdownElement = $('#event-view-template-modal-dropdown')
        $(dropdownElement).empty()
        jQuery.each(availableTemplates, function () {
            $('<option/>', {
                'value': this,
                'text': this
            }).appendTo(dropdownElement);
        });
    }

    function submitForm() {
        const selectedValue = $('#events-modal-mins-late-dropdown :selected').val()
    }

    function deleteSelectedValue() {
        const templateName = $('#event-view-template-modal-dropdown :selected').val()
        if (templateName) {
            let confirmDelete = confirm("Remove Template: " + templateName + "?")
            if (confirmDelete) {
                $templates.delete(templateName)
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
$('.event-view-save-template').click(function () {
    if (raid_event.currently_selected_boss_roster == -1) {
        status_alert(2000, "Needs a Selected Boss", "warning")
        return
    }
    let template_name = prompt("Name of Template: ")
    $templates.save(template_name)
})

// Load a template from modal
$('#template-modal-load').click(function () {
    let selected_value = $('#event-view-template-modal-dropdown :selected').val()
    templateModal.closeModal()
    if (selected_value) {
        $templates.load(selected_value)
    } else {
        status_alert(2000, "No such template exists", "warning")
    }
});

$templates = {
    /**
     * Save roster to localStorage
     * @param {string} template_name
     */
    save: function (template_name) {
        if (typeof (Storage) == "undefined") {
            status_alert(2000, "You don't have LocalStorage on your browser", "danger")
            return
        }
        // Quick name validation, must be between 1 and 25 chars
        if (template_name == null)
            return

        if (template_name.length < 1 || template_name.length > 25) {
            status_alert(2000, "Cannot Save: Invalid Name", "warning")
            return
        }

        let boss_id = raid_event.currentlySelectedRoster
        let roster_to_save = raid_event.rosterPerBossObjects[boss_id].selectedRoster

        // Check if roster contains characters
        if (roster_to_save.length < 1) {
            status_alert(2000, "Cannot Save: Roster is Empty", "danger")
            return
        }
        let jsonified_roster = JSON.stringify(roster_to_save)
        localStorage.setItem(template_name, jsonified_roster)


        let saved_roster_template_list = this.available_templates
        saved_roster_template_list.push(template_name)
        let jsonified_list = JSON.stringify(saved_roster_template_list)
        localStorage.setItem("saved_roster_template_list", jsonified_list)

        status_alert(2000, "Template Saved As: " + template_name, "success")
    },

    /**
     * Load a roster from localstorage
     * @param {string} template_name
     */
    load: function (template_name) {
        let roster_from_localstorage = localStorage.getItem(template_name)
        let parsed_roster = JSON.parse(roster_from_localstorage)

        let boss_id = raid_event.currentlySelectedRoster
        raid_event.rosterPerBossObjects[boss_id].load_roster_from_roster_list(parsed_roster)
        raid_event.rosterPerBossObjects[boss_id].display_selected_roster()
        raid_event.rosterPerBossObjects[boss_id].display_benched_roster()
        raid_event.rosterPerBossObjects[boss_id].display_buff_info()

        // When a roster is loaded, the setup is sent to db for saving
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
    },

    /**
     * Delete a roster from localstorage
     * @param {string} template_name
     */
    delete: function (template_name) {
        available_templates = this.available_templates
        let itemIndex = available_templates.indexOf(template_name)
        available_templates.splice(itemIndex, 1)
        localStorage.setItem("saved_roster_template_list", JSON.stringify(available_templates))
        localStorage.removeItem(template_name)

        templateModal.fillTemplateModalDropdown()
    },

    buttons: {
        update: function () {
            const save_button = $('.event-view-save-template')
            if (raid_event.rosterPerBossObjects[raid_event.currentlySelectedRoster].selectedRoster.length == 0) {
                $(save_button).addClass('ane-btn-disabled')
                $(save_button).removeClass('ane-btn-success')
            } else {
                $(save_button).addClass('ane-btn-success')
                $(save_button).removeClass('ane-btn-disabled')
            }
        },
    },

    get available_templates() {
        return JSON.parse(localStorage.getItem("saved_roster_template_list")) || []
    },
}