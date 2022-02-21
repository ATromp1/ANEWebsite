const IMAGES_PATH_ROLES = 'images/roleIcons/'
const IMAGES_PATH_CLASS = 'images/classIcons/'

// Rework the boss information we get from the DB into a more managable format
let boss_name_list = {}
for (i = 0; i < boss_list.length; i++) {
    boss_name_list[boss_list[i].fields.boss_id] = {
        'name': boss_list[i].fields.boss_name,
        'id': boss_list[i].fields.boss_id
    }
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

if(is_past_event){
    is_staff = false
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
        this.roster_per_boss_objects = {}

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
            this.bosses[boss]
            let current_roster = new RosterPerBoss(this.bosses[boss].id, this.initial_roster)
            this.roster_per_boss_objects[this.bosses[boss].id] = current_roster
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

    switch_to_summary(){
        if(this.currently_selected_boss_roster != -1){
            this.currently_selected_boss_roster = -1
            display_summary_view()
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
        this.empty_selected_roster()

        for(let i in selected_roster){
            let char = selected_roster[i]
            this.move_from_bench_to_selected(char.name,char.role)
        }
    }

    empty_selected_roster(){
        this.selected_roster = []
        this.benched_roster = this.initial_roster.slice()
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
        update_boss_buttons_status(this.boss)
    }

    move_from_selected_to_bench(char_name, display_change){
        display_change = false || display_change
        this.#add_char_to_benched_roster(char_name)
        this.#remove_char_from_selected_roster(char_name);
        if(display_change){
            this.display_benched_roster()
            this.display_selected_roster()
        }
        update_boss_buttons_status(this.boss)
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


        // First clear all old buttons
        $('.boss-view-btn').removeClass('active');

        // Highlights the button of the currently selected boss
        $('.boss-view-btn#'+this.boss).addClass('active')

        // Clear the table first
        $('.event-view-benched-roster-table').empty();

        let roles = ['tank', 'healer', 'mdps', 'rdps']
        let td_css_class = "event-view-role-icon"
        jQuery.each(this.benched_roster, function(){
            let $tr = $('<tr/>',{'class':'benched-roster-row'})

            $tr.append($('<td/>',{
                'class': css_classes[this.playable_class],
                'text': this.name
            }))

            // Don't append the role icons if user is not staff
            if(is_staff){
                for(let role in roles){
                    role = roles[role]
                    if(this.roles.includes(role)){
                        $tr.append($('<td/>',{
                            'id': role,
                            'class':'event-view-role-icon',
                            'html':$('<img/>',{
                                'src': static_url+IMAGES_PATH_ROLES+role+'.png',
                                'class':td_css_class,
                            })
                        }))
                    } else { $tr.append($('<td/>')) }
                }
            }
            $('.event-view-benched-roster-table').append($tr)

        });

    } 
}

function is_user_selected_for_boss(boss_id){
    if(typeof(user_event_summary[boss_id]) !== "undefined"){
        if(typeof(user_event_summary[boss_id].name) !== "undefined"){
            return true
        }
        return false
    }
    return false
}

function display_summary_view(){
    $('.event-view-boss-info').addClass('hidden')
    $('body').css('backgroundImage', 'url('+static_url+'images/bossImages/Sepulcher/SepulcherBG.jpg'+')')
    $('.event-view-header-bossname').text("Event Summary")
    $('.boss-view-btn').removeClass('active');


    $('.event-view-summary').removeClass("hidden")
    $('.event-view-summary').empty()

    let any_boss_is_shown = false
    jQuery.each(boss_name_list, function(){
        let players_in_boss_roster = raid_event.roster_per_boss_objects[this.id].selected_roster.length
        if(players_in_boss_roster>19){
            any_boss_is_shown = true
            let boss_div = ($('<div/>',{
                'class': 'event-view-summary-boss',
                'html':$('<span/>',{
                    'class': "event-view-summary-boss-name",
                    'text': this.name,
                })
            }))
            $('.event-view-summary').append(boss_div)

            // Check if the data we get from DB is valid
            if(typeof(user_event_summary[this.id]) !== "undefined"){
                if(typeof(user_event_summary[this.id].name) !== "undefined"){
                    let char = user_event_summary[this.id]
                    // Create a div to show role
                    let role_div = $('<div/>',{
                        'class':'event-view-summary-role',
                    })
                    boss_div.append(role_div)

                    role_div.append($('<img/>',{
                        'class':'event-view-summary-role-img',
                        'src':static_url+IMAGES_PATH_ROLES+char.role+'.png',
                    }))
                    role_div.append($('<span/>',{
                        'class':'event-view-summary-role-span',
                        'text':char.role
                    }))
                    // Create a div inside of boss-container
                    let char_name_div = ($('<div/>',{
                        'class':'event-view-summary-char-name'
                    }))
                    boss_div.append(char_name_div)

                    // Create the class image with char name next to it
                    char_name_div.append($('<img/>',{
                        'class':'event-view-summary-class-icon',
                        'src': static_url+IMAGES_PATH_CLASS+css_classes[char.playable_class]+'.png',
                    }))
                    char_name_div.append($('<span/>',{
                        'text':char.name,
                        'class': css_classes[char.playable_class]
                    }))
                } else {
                    // If the event doesn't have your name and you are not absent but there is a roster that means you are bench
                    boss_div.append($('<span/>',{
                        'class':'event-view-summary-benched',
                        'text':'Benched'
                    }))
                }
            }
        }
    });
    // For non-staff users. If no boss has a roster of atleast 20 people then show that to user
    if(!any_boss_is_shown){
        $('.event-view-summary').append($('<div/>',{
            'class': 'event-view-summary-boss',
            'html':$('<span/>',{
                'class': "event-view-summary-boss-name",
                'text': 'No boss has a selected roster yet',
            })
        }))
    }
    // If current user is absent then we don't show any bosses and just display absent
    if(user_is_absent){
        $('.event-view-summary').empty()
        $('.event-view-summary').append($('<div/>',{
            'class': 'event-view-summary-boss',
            'style': 'background-color:var(--danger-bg-color);padding:3px 5px;border-radius:0.25rem',
            'html':$('<span/>',{
                'class': "event-view-summary-boss-name",
                'text': 'You are Absent for this event',
            })
        }))
    }
}


// Create new raid_event and populate that object with rosters
raid_event = new RaidEvent(boss_name_list, roster_characters)
raid_event.populate_boss_rosters()
raid_event.load_rosters_from_db(boss_rosters)



//Create boss buttons
function create_boss_buttons(){
    jQuery.each(boss_name_list, function(){
        $('.event-view-boss-list').append($('<div/>',{
            'class':'boss-view-btn',
            'id':this.id,
            'text':this.name
        }));
    });
}

// Set the colour depending on the rosters status
function update_boss_buttons_status(boss_id){
    let boss_btn_element = $('.boss-view-btn#'+boss_id)

    $(boss_btn_element).removeClass('empty-roster in-progress roster-complete '+
    'empty-roster-staff in-progress-staff roster-complete-staff')
    let players_in_boss_roster = raid_event.roster_per_boss_objects[boss_id].selected_roster.length
    let boss_roster_status = ''
    if(is_staff){
        if(players_in_boss_roster == 0){
            boss_roster_status = 'empty-roster'
        } else if(players_in_boss_roster < 20){
            boss_roster_status = 'in-progress'
        } else {
            boss_roster_status = 'roster-complete'
        }
    } else{
        if(players_in_boss_roster>19){
            boss_roster_status = 'roster-complete'
        }
        if(!is_user_selected_for_boss(boss_id)){
            boss_roster_status = boss_roster_status + ' benched'
        }
    }
    $(boss_btn_element).addClass(boss_roster_status)
}

// Create buttons and update their status on page load
create_boss_buttons()
// Update all buttons atleast once on page load
for(let boss in raid_event.bosses){
    update_boss_buttons_status(raid_event.bosses[boss].id)
}
// Start page on summary
display_summary_view()
// Summary button
$('.event-view-summary-btn').click(function(){
    raid_event.switch_to_summary()
})


// If element with class '.boss-view-btn' gets clicked then get element id and call
// RaidEvent.switch_to_roster() with boss id same as button
$('.boss-view-btn').click(function(){
    $('.event-view-boss-info').removeClass('hidden')
    $('.event-view-summary').addClass("hidden")
    raid_event.switch_to_roster(this.id)
    let boss_image_path = get_boss_image_path_from_id(this.id)
    $('body').css('backgroundImage', 'url('+boss_image_path+')')
    $('.event-view-header-bossname').text(boss_name_list[this.id].name)
})

function get_boss_image_path_from_id(boss_id){
    let boss_name = boss_name_list[boss_id].name
    let stripped_boss_name = boss_name.replace(/[^A-Z0-9]/ig, "")
    return static_url+'images/bossImages/Sepulcher/'+stripped_boss_name + "BG.jpg"
}


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
        timeout: 1000,
    })
}