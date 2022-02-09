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
let class_roles =['tank', 'healer','mdps','rdps']

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
    constructor(bosses, initial_roster) {
        // Bosses in a raid
        this.bosses = bosses;

        // Initial roster is the roster we get from DB
        this.initial_roster = initial_roster;

        // instances of class RosterPerBoss in an array to access them
        this.roster_per_boss_objects = []

        // This should be a boss_id
        this.currently_selected_boss_roster = -1
    }


    populate_boss_rosters() {
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
            console.log("switch_to_roster bossid: " + boss_id)
            this.currently_selected_boss_roster = boss_id
            this.roster_per_boss_objects[boss_id].update_roster_display()
        }
    }


    get_bosses() {
        return this.bosses;
    }
}

class RosterPerBoss {
    constructor(boss, initial_roster) {
        this.boss = boss;
        this.initial_roster = initial_roster
        this.benched_roster = initial_roster
        this.selected_roster = []
    }



    update_roster_display(roster){
        /*
        This function doesn't change any variables, simply updates the display to this RosterPerBoss class
        It only updates the display
        */

        $('.event-view-available-roster-table').empty();
        // First clear all old buttons
        $('.boss-view-btn').removeClass('active');

        // Highlights the button of the currently selected boss
        $('.boss-view-btn#'+this.boss).addClass('active')

        let images_path = 'images/roleIcons/'
        for(let char in this.benched_roster){
            let char_name = this.benched_roster[char].name
            let char_css_class = css_classes[this.benched_roster[char].playable_class]

            let event_view_table_row =  '<tr>'+'<td class="'+char_css_class+'">'+char_name+'</td>'

            if(this.benched_roster[char].roles.includes('tank')){
                event_view_table_row = event_view_table_row + '<td><img src="'+static_url+images_path+'tank.png" alt="Tank"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            if(this.benched_roster[char].roles.includes('healer')){
                event_view_table_row = event_view_table_row + '<td><img src="'+static_url+images_path+'healer.png" alt="Healer"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            if(this.benched_roster[char].roles.includes('mdps')){
                event_view_table_row = event_view_table_row + '<td><img src="'+static_url+images_path+'mdps.png" alt="Melee dps"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            if(this.benched_roster[char].roles.includes('rdps')){
                event_view_table_row = event_view_table_row + '<td><img src="'+static_url+images_path+'rdps.png" alt="Ranged dps"></td>'
            }else{
                event_view_table_row = event_view_table_row + '<td></td>'
            }

            event_view_table_row = event_view_table_row + '</tr>';
            $('.event-view-available-roster-table').append(event_view_table_row);
        }
    }
}


raid_event = new RaidEvent(boss_name_list, roster_characters)
raid_event.populate_boss_rosters()


//Create boss buttons
let HTMLtoAppend = ''
for(i = 0; i < boss_name_list.length; i++){
    HTMLtoAppend = HTMLtoAppend + '<div class="boss-view-btn" id="'+boss_name_list[i].id+'">' + boss_name_list[i].name + '</div>'
}
$('.event-view-boss-list').append(HTMLtoAppend);

// If element with class '.boss-view-btn' gets clicked then get element id and call
// RaidEvent.switch_to_roster() with boss id same as button
$('.boss-view-btn').click(function(){
    raid_event.switch_to_roster(this.id)
})