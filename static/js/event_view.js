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
        this.bosses = bosses;
        this.initial_roster = initial_roster;

        this.roster_per_boss_objects = []
    }


    populate_boss_rosters() {
        for (let boss in this.bosses) {
            this.bosses[boss];
            let current_roster = new RosterPerBoss(this.bosses[boss].id, this.initial_roster)
            this.roster_per_boss_objects.push(current_roster)
        }

    }

    switch_to_roster(boss_id){
        console.log("switch_to_roster bossid: " + boss_id)
        roster_per_boss_objects[boss_id].update_roster_display()
    }


    get_bosses() {
        return this.bosses;
    }
}

class RosterPerBoss {
    constructor(boss, initial_roster) {
        this.boss = boss;
        this.initial_roster = initial_roster
        this.roster = []
    }

    populate_roster() {
        for (let character in this.initial_roster) {
            this.roster[character] = new RosterCharacter(this.initial_roster.name,
                this.initial_roster.playable_class,
                this.initial_roster.role)
        }
    }   

    update_roster_display(){
        $('.event-view-boss-info').empty();
        HTMLtoAppend = ''
        let roster = raid_event.roster_per_boss_objects[this.boss];
        HTMLtoAppend = HTMLtoAppend + roster.boss
        for(let char in roster.initial_roster){
            HTMLtoAppend = HTMLtoAppend +'<div class="'+ css_classes[roster.initial_roster[char].playable_class] +'">' + roster.initial_roster[char].name;
        
            for(let role in roster.initial_roster[char].roles){
                HTMLtoAppend = HTMLtoAppend + '<div class="event-view-role-icon" id="'+ roster.initial_roster[char].roles[role] +' '+ roster.initial_roster[char].name+'"></div>';
            }

            HTMLtoAppend = HTMLtoAppend + '</div>';
        
        }
        $('.event-view-boss-info').append(HTMLtoAppend);   
    }
}

class RosterCharacter {
    constructor(name, playable_class, role) {
        this.boss_name = boss_name;
        this.name = name;
        this.playable_class = playable_class;
        this.role = role;
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
// update_roster_display() with boss id same as button
$('.boss-view-btn').click(function(){
    raid_event.switch_to_roster(this.id)  // roster_per_boss_objects[this.id].update_roster_display()
})