/* eslint-disable prettier/prettier */
/* eslint-disable no-dupe-class-members */
/* eslint-disable no-undef */
const IMAGES_PATH_ROLES = 'images/roleIcons/'
const IMAGES_PATH_CLASS = 'images/classIcons/'

// Rework the boss information we get from the DB into a more managable format
let boss_name_list = []
for (i = 0; i < boss_list.length; i++) {
    boss_name_list.push({
        'name': boss_list[i].fields.boss_name,
        'id': i
    })
}

let roles_per_class = {
    'Warrior': ['tank', 'mdps'],
    'Paladin': ['tank', 'mdps', 'healer'],
    'Hunter': ['rdps', 'mdps'],
    'Rogue': ['mdps'],
    'Priest': ['rdps', 'healer'],
    'Shaman': ['rdps', 'mdps', 'healer'],
    'Mage': ['rdps'],
    'Warlock': ['rdps'],
    'Monk': ['tank', 'mdps', 'healer'],
    'Druid': ['tank', 'rdps', 'mdps', 'healer'],
    'Demon Hunter': ['tank', 'mdps'],
    'Death Knight': ['tank', 'mdps']
}


// Rework the roster information we get from the DB into a more managable format
let roster_characters = []
for (let i in roster) {
    let roles = roles_per_class[roster[i].playable_class]
    roster_characters.push({
        'name': roster[i].name,
        'playable_class': roster[i].playable_class,
        'roles': roles,
    })
}
 
class RaidEvent {
    /*
    Contains the information needed to display a roster for each boss
    */
    constructor(bosses, initial_roster) {
        // Bosses in a raid
        this.bosses = bosses;

        // Initial roster is the roster we get from DB
        this.initial_roster = initial_roster;

        // Objects of class RosterPerBoss in an array to access them
        this.roster_per_boss_objects = []

        // This should be a boss_id
        this.currently_selected_boss_roster = -1
    }
    get_playable_class_by_char_name(char_name){

        for(let i in this.initial_roster){
            let char = this.initial_roster[i]
            if(char.name == char_name){
                return char.playable_class
            }
        }
        return 'Character not in initial_roster'
    }

    load_rosters_from_db(boss_rosters){
        for(let boss in boss_rosters){
            let boss_id = boss
            let boss_roster = boss_rosters[boss]
            let selected_roster_for_boss = []

            for(let role in boss_roster){
                for(let char in boss_roster[role]){
                    let char_name = boss_roster[role][char]
                    let playable_class = this.get_playable_class_by_char_name(char_name)
                    selected_roster_for_boss.push({
                        'name': char_name,
                        'playable_class': playable_class,
                        'role': role,
                    })
                }
            }
            this.roster_per_boss_objects[boss_id].load_roster_from_roster_list(selected_roster_for_boss)
        }
    }


    populate_boss_rosters() {
        /*
        Create a new object of RosterPerBoss for each boss in the current RaidEvent
        */
        for (let boss in this.bosses) {
            this.bosses[boss];
            let current_roster = new RosterPerBoss(this.bosses[boss].id, this.initial_roster)
            this.roster_per_boss_objects.push(current_roster)
        }

    }

    switch_to_roster(boss_id){
        /*
        Switches to a different roster(boss) in the info view. Changes 'currently_selected_boss_roster' to the new boss
        */
        if(boss_id != this.currently_selected_boss_roster){
            this.currently_selected_boss_roster = boss_id
            this.roster_per_boss_objects[boss_id].display_benched_roster()
            this.roster_per_boss_objects[boss_id].display_selected_roster()
        }
    }
}

class RosterPerBoss {
    /*
    Contains an array of benched players and selected players and has functions to display them in seperate columns
    */
    constructor(boss, initial_roster) {
        this.boss = boss;
        this.initial_roster = initial_roster
        this.benched_roster = initial_roster.slice()
        this.selected_roster = []
    }

    load_roster_from_roster_list(selected_roster){
        for(let i in selected_roster){
            let char = selected_roster[i]
            this.move_from_bench_to_selected(char.name,char.role)
        }
    }
    #remove_char_from_benched_roster(char_name){
        for(let index in this.benched_roster){
            let char = this.benched_roster[index]
            if(char.name == char_name){
                this.benched_roster.splice(index,1)
                return index
            }
        }
    }   

    #add_char_to_benched_roster(char_name){
        for(let index in this.initial_roster){
            let char = this.initial_roster[index]
            if(char.name == char_name){
                this.benched_roster.push(char)
            }
        }
    }

    #remove_char_from_selected_roster(char_name){
        for(let index in this.selected_roster){
            let char = this.selected_roster[index]
            if(char.name == char_name){
                this.selected_roster.splice(index,1)
                return index
            }
        }
    }

    #add_char_to_selected_roster(char_name, role){
        // Assume char is in the benched roster.
        for(let index in this.benched_roster){
            let char = this.benched_roster[index]
            if(char.name == char_name){
                this.selected_roster.push({
                    'name': char.name,
                    'playable_class': char.playable_class,
                    'role': role,
                })
            }
        }
    }


    get_amount_of_role_in_selected_roster(role){
        let count = 0
        for(let index in this.selected_roster){
            let char = this.selected_roster[index]
            if(char.role == role){
                count++;
            }
        }
        return count
    }

    move_from_bench_to_selected(char_name, role, display_change){
        display_change = false || display_change
        this.#add_char_to_selected_roster(char_name, role);
        let char_removed_at_index = this.#remove_char_from_benched_roster(char_name)
        if(display_change){
            this.remove_from_benched_display_at_index(char_removed_at_index)
            this.display_selected_roster()
        }
        update_boss_buttons_status()
    }

    move_from_selected_to_bench(char_name, display_change){
        display_change = false || display_change
        this.#add_char_to_benched_roster(char_name)
        this.#remove_char_from_selected_roster(char_name);
        if(display_change){
            this.display_benched_roster()
            this.display_selected_roster()
        }
        update_boss_buttons_status()
    }

    remove_from_benched_display_at_index(index){
        let element_to_remove = $('.event-view-benched-roster-table .benched-roster-row').eq(index)
        element_to_remove.remove()
    }


    display_selected_roster(){
        let header_element_tank = $('.event-view-selected-roster-header').eq(0);
        let header_element_healer = $('.event-view-selected-roster-header').eq(1);
        let header_element_mdps = $('.event-view-selected-roster-header').eq(2);
        let header_element_rdps = $('.event-view-selected-roster-header').eq(3);

        
        $('.event-view-selected-roster-tank, '+
          '.event-view-selected-roster-healer, '+
          '.event-view-selected-roster-mdps, '+
          '.event-view-selected-roster-rdps').empty()

        $('.event-view-selected-roster-tank').append(header_element_tank)
        $('.event-view-selected-roster-healer').append(header_element_healer)
        $('.event-view-selected-roster-mdps').append(header_element_mdps)
        $('.event-view-selected-roster-rdps').append(header_element_rdps)

        if(this.selected_roster.length > 20){
            $('.event-view-selected-roster-totalcount').addClass('overcapacity')
        }else{
            $('.event-view-selected-roster-totalcount').removeClass('overcapacity')
        }
        $('.event-view-selected-roster-totalcount').text('Total: '+this.selected_roster.length)
        $('.event-view-selected-roster-tankcount').text(' - ' + this.get_amount_of_role_in_selected_roster('tank'))
        $('.event-view-selected-roster-healercount').text(' - ' + this.get_amount_of_role_in_selected_roster('healer'))
        $('.event-view-selected-roster-mdpscount').text(' - ' + this.get_amount_of_role_in_selected_roster('mdps'))
        $('.event-view-selected-roster-rdpscount').text(' - ' + this.get_amount_of_role_in_selected_roster('rdps'))

        let additional_staff_info = ''
        if(is_staff){
            additional_staff_info = ' class="is-staff"'
        }
        for(let index in this.selected_roster){

            let char = this.selected_roster[index]
            $('.event-view-selected-roster-'+char.role).append('<div class="'+css_classes[char.playable_class]+' event-view-selected-roster-char">'+
            '<img src="'+static_url+IMAGES_PATH_CLASS+css_classes[char.playable_class]+'.png" alt="Tank" class="event-view-role-icon">'+
            '<span'+additional_staff_info+'>'+char.name+'</span></div>')

        }
    }

    display_benched_roster(){
        /*
        This function doesn't change any variables, simply updates the display to this RosterPerBoss class
        It only updates the display
        */

        $('.event-view-benched-roster-table').empty();
        // First clear all old buttons
        $('.boss-view-btn').removeClass('active');

        // Highlights the button of the currently selected boss
        $('.boss-view-btn#'+this.boss).addClass('active')

        for(let char in this.benched_roster){
            let char_name = this.benched_roster[char].name
            let char_css_class = css_classes[this.benched_roster[char].playable_class]

            let event_view_table_row =  '<tr class="benched-roster-row">'+'<td class="'+char_css_class+'">'+char_name+'</td>'

            if(this.benched_roster[char].roles.includes('tank')){
                event_view_table_row = event_view_table_row + '<td id="tank"><img src="'+static_url+IMAGES_PATH_ROLES+'tank.png" alt="Tank" class="event-view-role-icon"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            if(this.benched_roster[char].roles.includes('healer')){
                event_view_table_row = event_view_table_row + '<td id="healer"><img src="'+static_url+IMAGES_PATH_ROLES+'healer.png" alt="Healer" class="event-view-role-icon"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            if(this.benched_roster[char].roles.includes('mdps')){
                event_view_table_row = event_view_table_row + '<td id="mdps"><img src="'+static_url+IMAGES_PATH_ROLES+'mdps.png" alt="Melee dps" class="event-view-role-icon"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            if(this.benched_roster[char].roles.includes('rdps')){
                event_view_table_row = event_view_table_row + '<td id="rdps"><img src="'+static_url+IMAGES_PATH_ROLES+'rdps.png" alt="Ranged dps" class="event-view-role-icon"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            event_view_table_row = event_view_table_row + '</tr>';
            $('.event-view-benched-roster-table').append(event_view_table_row);
        }
    }
}


raid_event = new RaidEvent(boss_name_list, roster_characters)
raid_event.populate_boss_rosters()
raid_event.load_rosters_from_db(boss_rosters)



//Create boss buttons
function create_boss_buttons(){
    let HTMLtoAppend = ''
    for(i = 0; i < boss_name_list.length; i++){
        let boss_id = boss_name_list[i].id
        let boss_name = boss_name_list[i].name
        HTMLtoAppend = HTMLtoAppend + '<div class="boss-view-btn" id="'+ boss_id +'">' + boss_name + '</div>'
    }
    $('.event-view-boss-list').append(HTMLtoAppend);
}
create_boss_buttons()

// Set the colour depending on the rosters status
function update_boss_buttons_status(){
    for(let boss in raid_event.bosses){
        boss_id = raid_event.bosses[boss].id
        let boss_btn_element = $('.boss-view-btn').eq(boss_id)

        $(boss_btn_element).removeClass('empty-roster in-progress roster-complete')

        let players_in_boss_roster = raid_event.roster_per_boss_objects[boss_id].selected_roster.length
        let boss_roster_status = ''
        if(players_in_boss_roster == 0){
            boss_roster_status = 'empty-roster'
        } else if(players_in_boss_roster < 20){
            boss_roster_status = 'in-progress'
        } else {
            boss_roster_status = 'roster-complete'
        }
        
        $(boss_btn_element).addClass(boss_roster_status)
    }
}
update_boss_buttons_status()
// If element with class '.boss-view-btn' gets clicked then get element id and call
// RaidEvent.switch_to_roster() with boss id same as button
$('.boss-view-btn').click(function(){
    raid_event.switch_to_roster(this.id)
})

/* 
Sets a click event listener on benched-roster table td elements.
If it has id then id will be role, char_name will always be the first sibling of type td
Sends ajax request to the server to sync up the database
Doesnt need a staff check as it is not displayed unless you're staff member
*/
$('.event-view-benched-roster').on('click', '.benched-roster-row td', function(){
    if(this.id){
        role = this.id
        char_name = jQuery(this).siblings('td').first()[0].innerHTML
        current_boss_id = raid_event.currently_selected_boss_roster
        raid_event.roster_per_boss_objects[current_boss_id].move_from_bench_to_selected(char_name, role, true)

        char_moved_ajax(char_name, role, current_boss_id)
    }
})

/*
 Same as above but removes the character from selected instead
*/
if(is_staff){
    $('.event-view-selected-roster').on('click','.event-view-selected-roster-char span', function(){
        char_name = this.innerHTML
        current_boss_id = raid_event.currently_selected_boss_roster
        role = this.parentElement.parentElement.id
        raid_event.roster_per_boss_objects[current_boss_id].move_from_selected_to_bench(char_name, role, true)

        char_moved_ajax(char_name, role, current_boss_id)
    })
}

function char_moved_ajax(char_name, role, current_boss_id){
    $.ajax({
        url: window.location.href,
        data: {
            'name': char_name,
            'role': role,
            'boss_id': current_boss_id,
        },
        dataType: 'json',
    })
}


/* /.................// Roster Templates //................./ */

$('.event-view-save-template').click(function(){
    if(raid_event.currently_selected_boss_roster == -1){
        status_alert(2000, "Needs a Selected Boss", "warning")
        return
    }
    let template_name = prompt("Name of Template: ")
    save_roster_template(template_name)
})

$('.event-view-load-template').click(function(){
    if(raid_event.currently_selected_boss_roster == -1){
        status_alert(2000, "Needs a Selected Boss", "warning")
        return
    }
    toggle_template_load_modal()
})

$('#template-modal-close').click(function(){toggle_template_load_modal()})


$('#template-modal-load').click(function(){
    let selected_value = $('#event-view-template-modal-dropdown :selected').val()
    toggle_template_load_modal()
    load_roster_template(selected_value)
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
    status_alert(2000, "Template Loaded: " + template_name, "success")

    $.ajax({
        url: window.location.href,
        data: {
            'saved_setup': roster_from_localstorage,
            'boss_id': boss_id,
        },
        dataType: 'json',
        contentType: "application/json",
    })
}