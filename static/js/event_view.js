const IMAGES_PATH_ROLES = 'images/roleIcons/'
const IMAGES_PATH_CLASS = 'images/classIcons/'
const IMAGES_PATH_BUFFS = 'images/buffIcons/'
const ROLES_PER_CLASS = {
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
const CLASS_BUFFS = [
    {
        'playable_class':'Warrior',
        'buff_name':'battle_shout'
    },
    {
        'playable_class': 'Priest',
        'buff_name': 'fortitude',
    },
    {
        'playable_class':'Mage',
        'buff_name':'intellect',
    },
    {
        'playable_class':'Warlock',
        'buff_name':'soulstone',
    },
    {
        'playable_class':'Monk',
        'buff_name':'mystic_touch',
    },
    {
        'playable_class':'Demon Hunter',
        'buff_name':'chaos_brand',
    },
    {
        'playable_class':'Shaman',
        'buff_name':'windfury',
    },
]

let bossNameList = boss_list_db_to_object(boss_list)
let rosterCharacters = roster_list_db_to_object(roster)

if(is_past_event){
    // is_past_event is variable sent through from backend. If true then we disable staff so group can't be altered
    is_staff = false
}

class RaidEvent {
    /*
    Contains the information needed to display a roster for each boss
    */
    constructor(bosses, initialRoster) {
        // Bosses in a raid
        this.bosses = bosses;

        // Initial roster is the roster we get from DB
        this.initialRoster = initialRoster;

        // Objects of class RosterPerBoss in an array to access them
        this.rosterPerBossObjects = {}

        // This should be a boss_id
        this.currentlySelectedRoster = -1
    }
    get_playable_class_by_char_name(charName){
        for(let i in this.initialRoster){
            let char = this.initialRoster[i]
            if(char.name == charName){
                return char.playable_class
            }
        }
        return 'Character not in initial_roster'
    }

    load_rosters_from_db(bossRosters){
        for(let boss in bossRosters){
            let boss_id = boss
            let boss_roster = bossRosters[boss]
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
            this.rosterPerBossObjects[boss_id].load_roster_from_roster_list(selected_roster_for_boss)
        }
    }

    update_published_status(bossRosters){
        for(let boss in bossRosters){
            // This is kinda shit but otherwise i dont know how to send through a False/True value through django
            if(bossRosters[boss].published == 'False'){
                this.rosterPerBossObjects[boss].published = false
            } else {
                this.rosterPerBossObjects[boss].published = true
            }
        }
    }

    populate_boss_rosters() {
        /*
        Create a new object of RosterPerBoss for each boss in the current RaidEvent
        */
        for (let boss in this.bosses) {
            this.bosses[boss]
            let current_roster = new RosterPerBoss(this.bosses[boss].id, this.initialRoster)
            this.rosterPerBossObjects[this.bosses[boss].id] = current_roster
        }

    }

    switch_to_roster(bossId){
        /*
        Switches to a different roster(boss) in the info view. Changes 'currently_selected_boss_roster' to the new boss
        */
        if(bossId != this.currentlySelectedRoster){
            this.currentlySelectedRoster = bossId
            let RosterPerBoss = this.rosterPerBossObjects[bossId]
            RosterPerBoss.display_benched_roster()
            RosterPerBoss.display_selected_roster()
            RosterPerBoss.display_buff_info()
            if(is_staff) RosterPerBoss.display_published_status()
            setLastVisitedBossView(this.currentlySelectedRoster)
        }
    }

    switch_to_summary(){
        if(this.currentlySelectedRoster != -1){
            this.currentlySelectedRoster = -1
            display_summary_view()
            setLastVisitedBossView(null)
        }
    }

    publishEvent(){
        $.ajax({
            data: {
                'type':'publish_event',
                'publish': 'True',
            },
            dataType: 'json',
            timeout: 1000,
        })
        this.updatePublishStatusFromButton(true)
        status_alert(2000, "Groups Published", "success")
    }
    undoPublication(){
        $.ajax({
            data: {
                'type':'publish_event',
                'publish': 'False',
            },
            dataType: 'json',
            timeout: 1000,
        })
        this.updatePublishStatusFromButton(false)
        status_alert(2000, "Publication revoked", "success")
    }

    updatePublishStatusFromButton(publish){
        for(const[key,value] of Object.entries(this.bosses)){
            this.rosterPerBossObjects[value.id].published=publish
        }
        if(this.currentlySelectedRoster != -1)
            this.rosterPerBossObjects[this.currentlySelectedRoster].display_published_status()
    }
}

class RosterPerBoss {
    /*
    Contains an array of benched players and selected players and has functions to display them in seperate columns
    */
    constructor(boss, initialRoster) {
        this.boss = boss;
        this.published = false
        this.initialRoster = initialRoster
        this.benchedRoster = initialRoster.slice()
        this.selectedRoster = []
        this.accountIdsInRoster = []
    }

    load_roster_from_roster_list(selectedRoster){
        this.empty_selected_roster()

        for(let i in selectedRoster){
            let char = selectedRoster[i]
            this.move_from_bench_to_selected(char.name,char.role)
        }
    }

    empty_selected_roster(){
        this.selectedRoster = []
        this.benchedRoster = this.initialRoster.slice()
    }

    remove_char_from_benched_roster(charName){
        for(let index in this.benchedRoster){
            let char = this.benchedRoster[index]
            if(char.name == charName){
                this.benchedRoster.splice(index,1)
                return index
            }
        }
    }   

    add_char_to_benched_roster(charName){
        for(let index in this.initialRoster){
            let char = this.initialRoster[index]
            if(char.name == charName){
                this.benchedRoster.push(char)
            }
        }
    }

    remove_char_from_selected_roster(charName){
        for(let index in this.selectedRoster){
            let char = this.selectedRoster[index]
            if(char.name == charName){
                this.accountIdsInRoster = removeValueFromArray(this.accountIdsInRoster, char.account_id)
                this.selectedRoster.splice(index,1)
                break
            }
        }
    }

    add_char_to_selected_roster(charName, role){
        // Assume char is in the benched roster.
        for(let index in this.benchedRoster){
            let char = this.benchedRoster[index]
            if(char.name == charName){
                this.selectedRoster.push({
                    'name': char.name,
                    'playable_class': char.playable_class,
                    'role': role,
                    'account_id': char.account_id,
                })
                if(!this.accountIdsInRoster.includes(char.account_id)) this.accountIdsInRoster.push(char.account_id)
            }
        }
    }

    get_amount_of_role_in_selected_roster(role){
        let count = 0
        for(let index in this.selectedRoster){
            let char = this.selectedRoster[index]
            if(char.role == role){
                count++;
            }
        }
        return count
    }

    move_from_bench_to_selected(charName, role, displayChange){
        displayChange = false || displayChange
        this.add_char_to_selected_roster(charName, role);
        this.remove_char_from_benched_roster(charName)
        if(displayChange){
            //this.remove_from_benched_display_at_index(char_removed_at_index)
            this.display_benched_roster()
            this.display_selected_roster()
            this.display_buff_info()
        }
        update_boss_buttons_status(this.boss)
    }

    move_from_selected_to_bench(charName, displayChange){
        displayChange = false || displayChange
        this.add_char_to_benched_roster(charName)
        this.remove_char_from_selected_roster(charName);
        if(displayChange){
            this.display_benched_roster()
            this.display_selected_roster()
            this.display_buff_info()
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

        if(this.selectedRoster.length > 20){
            $('.event-view-selected-roster-totalcount').addClass('overcapacity')
        }else{
            $('.event-view-selected-roster-totalcount').removeClass('overcapacity')
        }
        $('.event-view-selected-roster-totalcount').text('Total: '+this.selectedRoster.length)
        $('.event-view-selected-roster-tankcount').text(' - ' + this.get_amount_of_role_in_selected_roster('tank'))
        $('.event-view-selected-roster-healercount').text(' - ' + this.get_amount_of_role_in_selected_roster('healer'))
        $('.event-view-selected-roster-mdpscount').text(' - ' + this.get_amount_of_role_in_selected_roster('mdps'))
        $('.event-view-selected-roster-rdpscount').text(' - ' + this.get_amount_of_role_in_selected_roster('rdps'))

        let additional_staff_info = ''
        if(is_staff){
            additional_staff_info = ' class="is-staff"'
        }
        for(let index in this.selectedRoster){

            let char = this.selectedRoster[index]
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
        const ROSTER_TABLE = $('.event-view-benched-roster-table')
        $(ROSTER_TABLE).empty();

        const ALREADY_SELECTED = $('<div/>',{
            'class':'py-2',
            'style': 'margin-left:0.4rem; margin-bottom:0;',
            //'text': "Alts"
        })
        $(ROSTER_TABLE).append(ALREADY_SELECTED)
        
        let groupedRoster = groupBy(this.benchedRoster, 'playable_class')
        const ROLES = ['tank', 'healer', 'mdps', 'rdps']
        const TD_CSS_CLASSES = "event-view-role-icon"
        for(let i in groupedRoster){
            let playable_class = groupedRoster[i]
            playable_class.forEach((char)=>{
                let $tr = $('<tr/>',{'class':'benched-roster-row'})
                const accountIdInRoster = this.accountIdsInRoster.includes(char.account_id) ? char.account_id != "" : undefined
                if(accountIdInRoster){
                    $tr.append($('<td/>',{
                        'class': "text-secondary",
                        'text': char.name
                    }))
                } else {
                    let bossWish = char.wishes[raid_event.currentlySelectedRoster] || '-'
                    $tr.append($('<td/>',{
                        'class': css_classes[char.playable_class],
                        'text': char.name
                    }))
                    // If is staff append the boss wishes to the character
                    if(is_staff){
                        let bossWishCssClass;
                        if(bossWish == '99'){
                            bossWishCssClass = 'text-secondary'
                        } else if (bossWish == '0'){
                            bossWishCssClass = 'text-danger'
                        } else {
                            bossWishCssClass = ''
                        }
                        $tr.append($('<td/>', {
                            style: 'width:3rem;',
                            class: bossWishCssClass,
                            text: ` [ ${bossWish} ]`,
                        }))
                    }
                }   
    
                // Don't append the role icons if user is not staff
                if(is_staff){
                    if(!accountIdInRoster){
                        for(let role in ROLES){
                            role = ROLES[role]
                            if(char.roles.includes(role)){
                                $tr.append($('<td/>',{
                                    'id': role,
                                    'class':'event-view-role-icon',
                                    'html':$('<img/>',{
                                        'src': static_url+IMAGES_PATH_ROLES+role+'.png',
                                        'class':TD_CSS_CLASSES,
                                    })
                                }))
                            } else { $tr.append($('<td/>')) }
                        }
                    } else {
                        let charInRoster = this.getAccountsCharInRoster(char.account_id)
                        const $td = $('<td/>',{
                            'class':'position-absolute',
                            'text': "In as: "
                        })
                        $td.append($('<span/>',{
                            'class': css_classes[charInRoster.playable_class],
                            'text': charInRoster.name,
                        }))
                        $tr.append($td)
                    }
                }
    
                if(accountIdInRoster){
                    $(ROSTER_TABLE).append($tr)
                } else {
                    $(ROSTER_TABLE).prepend($tr)
                }
                
            })
        }
    }
    
    getAccountsCharInRoster(account_id){
        let charInRoster
        this.selectedRoster.forEach((char) => {
            if(char.account_id == account_id){
                charInRoster = char
            }
        })
        return charInRoster || ""
    }

    classes_in_roster(){
        let classes_in_roster = []
        jQuery.each(this.selectedRoster, function(){
            if(!classes_in_roster.includes(this.playable_class)){
                classes_in_roster.push(this.playable_class)
            }
        })
        return classes_in_roster
    }

    windfuryInRoster(){
        let windfuryInRoster = false
        this.selectedRoster.forEach((char)=>{
            if(char.playable_class == 'Shaman'){
                if(char.role == 'mdps'){
                    windfuryInRoster = true
                }
            }
        })
        return windfuryInRoster
    }

    display_buff_info(){
        if(is_staff){
            $('.event-view-buff-info').empty()
            $('.event-view-buff-info').append($('<div/>',{
                'text':'Missing Buffs',
                'class':'event-view-missing-buffs-text',
            }))
            let classes_in_roster = this.classes_in_roster()
            let noBuffIsShown = true
            CLASS_BUFFS.forEach((buff)=>{
                if(buff.playable_class == 'Shaman'){
                    if(!this.windfuryInRoster()){
                        appendBuff(buff)
                        noBuffIsShown = false
                    }
                } else if(!classes_in_roster.includes(buff.playable_class)){
                    noBuffIsShown = false
                    appendBuff(buff)
                }
            })

            function appendBuff(buff){
                const $buffDiv = $('<div/>',{'class':'event-view-buff'})
                $buffDiv.append($('<img/>',{
                    'class': 'event-view-buff-icon',
                    'src': static_url+IMAGES_PATH_BUFFS+buff.buff_name+'.png',
                }))
                $buffDiv.append($('<span/>',{
                    'id': buff,
                    'class':'event-view-buff-text',
                    'text': unslugify_string(buff.buff_name),
                }))
                $('.event-view-buff-info').append($buffDiv)
            }

            if(noBuffIsShown){
                $('.event-view-buff-info').append($('<span/>',{
                    'text': 'All Buffs in Group'
                }))
            }
            
        }
    }

    display_published_status(){
        if(!is_staff) return
        const publishDiv = $('.event-view-published-information')
        publishDiv.empty()
        if(this.published){
            const publishButton = $('<button/>',{
                'class': 'publish-button publish ane-btn ane-btn-warning py-2',
                'text': 'Undo Publication',
            })
            publishDiv.append(publishButton, $('<span/>', {
                'text': 'This group has been published'
            }))
            $(publishButton).click(() => { this.undo_publication() })
        } else {
            const publishButton = $('<button/>',{
                'class': 'publish-button undo-publish ane-btn ane-btn-success py-2',
                'text': 'Publish Group',
            })
            publishDiv.append(publishButton, $('<span/>', {
                'text': 'This group has NOT been published'
            }))
            $(publishButton).click(() => { this.publish_boss() })
        }
    }

    publish_boss(){
        if(this.selectedRoster.length == 0){
            status_alert(2000, "You can't publish an empty group", "warning")
        } else {
            $.ajax({
                data: {
                    'boss_id': this.boss,
                    'publish': 'True',
                },
                dataType: 'json',
                timeout: 1000,
            })
            this.published = true
            this.display_published_status()
            status_alert(2000, "Group Published", "success")
        }
    }

    undo_publication(){
        $.ajax({
            data: {
                'boss_id': this.boss,
                'publish': 'False',
            },
            dataType: 'json',
            timeout: 1000,
        })
        this.published = false
        this.display_published_status()
        status_alert(2000, "Publication revoked", "success")
    }
}

function create_summary_view(){
    let summary_boss_container = $('<div/>',{
        'class': 'summary-boss-container d-flex justify-content-center'
    })
    $('.event-view-summary').append(summary_boss_container)
    
    let any_boss_is_shown = false
    jQuery.each(bossNameList, function(){
        let players_in_boss_roster = raid_event.rosterPerBossObjects[this.id].selectedRoster.length
        if(raid_event.rosterPerBossObjects[this.id].published){
            any_boss_is_shown = true
            let boss_div = ($('<div/>',{
                'class': 'event-view-summary-boss',
                'html':$('<span/>',{
                    'class': "event-view-summary-boss-name",
                    'text': this.name,
                })
            }))
            if(!user_is_absent) $(summary_boss_container).append(boss_div)

            // Check if the data we get from DB is valid
            if(typeof(user_event_summary[this.id]) !== "undefined"){
                if(typeof(user_event_summary[this.id].name) !== "undefined"){
                     let char = user_event_summary[this.id]
                     append_boss_summary(boss_div, char, players_in_boss_roster)
                } else {
                    // If the event doesn't have your name and you are not absent but there is a roster that means you are bench
                    boss_div.append($('<span/>',{
                        'class':'event-view-summary-benched',
                        'text':'Benched'
                    }))
                    if(players_in_boss_roster<20){
                        boss_div.append($('<p/>',{
                            'text': "Note, this group is not complete",
                            'class': "text-center m-auto text-secondary w-75"
                        }))
                    }
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
    // If current user remove bosses on summary
    if(user_is_absent){
        //$('.event-view-summary').empty()
    }
    if(is_staff){
        create_officer_summary_information()
        create_great_vault()
    }
}

function create_officer_summary_information(){
    const OFFICER_SUMMARY_DIV = ($('<div/>',{
            'class': "event-view-summary-officer-info m-auto d-flex",
        })
    )
    createPublishEventButtons(OFFICER_SUMMARY_DIV)
    $('.event-view-summary').append(OFFICER_SUMMARY_DIV)
    let missing_users = $('.event-view-missing-users').clone()
    $(OFFICER_SUMMARY_DIV).append(missing_users)
}
function createPublishEventButtons(elementToAppendTo){
    const PUBLISH_BUTTON = $('<button/>',{
        'class': 'publish-button undo-publish ane-btn ane-btn-success',
        'text': 'Publish Groups',
    })
    const UNDO_PUBLISH_BUTTON = $('<button/>',{
        'class': 'publish-button undo-publish ane-btn ane-btn-warning',
        'text': 'Undo Publish',
    })
    const PUBLISH_BUTTONS_DIV = $('<div/>',{
        'class': 'publish-buttons-container',
    })
    PUBLISH_BUTTONS_DIV.append(PUBLISH_BUTTON, UNDO_PUBLISH_BUTTON)
    PUBLISH_BUTTONS_DIV.append($('<span/>',{
        'class': 'text-secondary',
        'text':'Note, these buttons will override any previous selections'
    }))
    elementToAppendTo.append(PUBLISH_BUTTONS_DIV)

    $(PUBLISH_BUTTON).click(()=>{
        raid_event.publishEvent()
    })
    $(UNDO_PUBLISH_BUTTON).click(()=>{
        raid_event.undoPublication()
    })
}

function display_summary_view(){
    $('.event-view-boss-info').addClass('hidden')
    $('body').css('backgroundImage', 'url('+static_url+'images/bossImages/Sepulcher/SepulcherBG.jpg'+')')
    $('.event-view-header-bossname').text("Event Summary")
    $('.boss-view-btn').removeClass('active');
    $('.event-view-summary').removeClass("hidden")
    display_player_summary()
}

function display_officer_summary_information(){
    $('.event-view-summary > div').addClass('hidden')
    $('.officer-summary-buttons > div').removeClass('active')
    $('.officer-extra-information').addClass('active')
    $('.officer-summary-buttons, .event-view-summary-officer-info').removeClass('hidden')
}

function display_vault_information(){
    $('.event-view-summary > div').addClass('hidden')
    $('.officer-summary-buttons > div').removeClass('active')
    $('.officer-vault-info').addClass('active')
    $('.officer-summary-buttons, .summary-vault-info').removeClass('hidden')
}

function display_player_summary(){
    $('.event-view-summary > div').addClass('hidden')
    $('.officer-summary-buttons > div').removeClass('active')
    $('.officer-player-summary').addClass('active')
    $('.officer-summary-buttons, .summary-boss-container').removeClass('hidden')
}

function append_boss_summary(boss_div, char, players_in_boss_roster){
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
    if(players_in_boss_roster<20){
        char_name_div.append($('<p/>',{
            'text': "Note, this group is not complete",
            'class': "text-center m-auto text-secondary w-75"
        }))
    }
}

function create_new_raid_event(){
    // Create new raid_event and populate that object with rosters
    raid_event = new RaidEvent(bossNameList, rosterCharacters)
    raid_event.populate_boss_rosters()
    raid_event.load_rosters_from_db(boss_rosters)
    raid_event.update_published_status(boss_rosters)
}
create_new_raid_event()


function create_boss_buttons(){
    jQuery.each(bossNameList, function(){
        $('.event-view-boss-list').append($('<div/>',{
            'class':'boss-view-btn ane-btn',
            'id':this.id,
            'text':this.name
        }));
    });
}

function update_boss_buttons_status(boss_id){
    // Set the colour depending on the rosters status
    let boss_btn_element = $('.boss-view-btn#' + boss_id)

    $(boss_btn_element).removeClass('empty-roster in-progress roster-complete '+
    'empty-roster-staff in-progress-staff roster-complete-staff')
    let players_in_boss_roster = raid_event.rosterPerBossObjects[boss_id].selectedRoster.length
    let boss_roster_status = ''
    if(is_staff){
        if(players_in_boss_roster == 0){
            boss_roster_status = 'empty-roster'
        } else if(players_in_boss_roster < 20){
            boss_roster_status = 'in-progress'
        } else {
            boss_roster_status = 'roster-complete'
        }
    } else if(raid_event.rosterPerBossObjects[boss_id].published){
            boss_roster_status = 'roster-complete'
        if(!is_user_selected_for_boss(boss_id)){
            boss_roster_status = boss_roster_status + ' benched'
        }
    }
    $(boss_btn_element).addClass(boss_roster_status)
}

// Create buttons and update their status on page load
create_boss_buttons()

for(let boss in raid_event.bosses){
    // Update all buttons atleast once on page load
    update_boss_buttons_status(raid_event.bosses[boss].id)
}

// Start page on summary
create_summary_view()
display_summary_view()

$('.event-view-summary-btn').click(function(){
    // Summary button
    raid_event.switch_to_summary()
})
if(is_staff){
$('.officer-player-summary').click(function(){
    display_player_summary()
})
$('.officer-extra-information').click(function(){
    display_officer_summary_information()
})
$('.officer-vault-info').click(function(){
    display_vault_information()
})
}

$('.boss-view-btn').click(function(){
    // If element with class '.boss-view-btn' gets clicked then get element id and call
    // RaidEvent.switch_to_roster() with boss id same as button
    changeBossView(this.id)
})

function changeBossView(bossId){
    $('.event-view-boss-info').removeClass('hidden')
    $('.event-view-summary').addClass("hidden")
    raid_event.switch_to_roster(bossId)
    swap_background_image(bossId)
}
function swap_background_image(bossId){
    let boss_image_path = get_boss_image_path_from_id(bossId)
    $('body').css('backgroundImage', 'url('+boss_image_path+')')
    $('.event-view-header-bossname').text(bossNameList[bossId].name)
}
function get_boss_image_path_from_id(bossId){
    let boss_name = bossNameList[bossId].name
    let stripped_boss_name = boss_name.replace(/[^A-Z0-9]/ig, "")
    return static_url+'images/bossImages/Sepulcher/'+stripped_boss_name + "BG.jpg"
}

if(is_staff){
    /* 
    Sets a click event listener on benched-roster table td elements.
    If it has id then id will be role, char_name will always be the first sibling of type td
    Sends ajax request to the server to sync up the database
    */
    $('.event-view-benched-roster').on('click', '.benched-roster-row td', function(){
        if(this.id){
            role = this.id
            // Remove the following: ] [ - 'whitespace' numbers 0-9
            const regex = /[\[\]\s\-0-9']/g
            char_name = jQuery(this).closest('.benched-roster-row').first().text().replace(regex, '')
            current_boss_id = raid_event.currentlySelectedRoster
            raid_event.rosterPerBossObjects[current_boss_id].move_from_bench_to_selected(char_name, role, true)
            char_moved_ajax(char_name, role, current_boss_id)
        }
    })

    /*
    Sets a click event listener on selected roster elements.
    Sends ajax request to the server to sync up the database
    */
    $('.event-view-selected-roster').on('click','.event-view-selected-roster-char span', function(){
        char_name = this.innerHTML
        current_boss_id = raid_event.currentlySelectedRoster
        role = this.parentElement.parentElement.id
        raid_event.rosterPerBossObjects[current_boss_id].move_from_selected_to_bench(char_name, role, true)
        char_moved_ajax(char_name, role, current_boss_id)
    })
}

