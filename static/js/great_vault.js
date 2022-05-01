function create_great_vault() {
    const roster_list = roster_list_db_to_object(roster)
    const vault_list = get_great_vault_list(roster_list)
    const MAX_VAULT_BOSSES_KILLED = 8
    const VAULT_THRESHOLD_CSS_CLASS = {
        '0': 'text-danger',
        '1': 'text-warning',
        '2': 'text-info',
        '3': 'text-success'
    }
    const summary_vault_info = ($('<div/>', {
        'class': "summary-vault-info m-auto",
        'html': $('<span/>', {
            'class': 'd-block h2 vault-header',
            'text': "The Great Vault",
        })
    }))
    $('.event-view-summary').append(summary_vault_info)

    let threshold_1_count = 0
    let threshold_2_count = 0
    let threshold_3_count = 0

    vault_list.forEach((char, index) => {
        const char_div = ($('<div/>', {
            'class': 'great-vault-char d-flex '
        }))
        summary_vault_info.append(char_div)

        char_div.append($('<div/>', {
            'class': 'great-vault-name ' + css_classes[get_playable_class_by_char_name(char.char_name)],
            'text': char.char_name
        }))
        const boss_rects = ($('<div/>', {
            'class': 'great-vault-boss-rects d-flex'
        }))
        char_div.append(boss_rects)

        for (i = 0; i < MAX_VAULT_BOSSES_KILLED; i++) {
            if (char.bosses_killed > i) {
                boss_rects.append($('<div/>', {
                    'text': "",
                    'class': "great-vault-boss-rect killed"
                }))
            } else {
                boss_rects.append($('<div/>', {
                    'text': "",
                    'class': "great-vault-boss-rect"
                }))
            }
        }
        char_div.append($('<div/>', {
            'class': 'great-vault-options',
            'text': char.bosses_killed
        }))
        let vault_options = get_vault_options_for_char(char.char_name)
        char_div.append($('<div/>', {
            'class': VAULT_THRESHOLD_CSS_CLASS[vault_options],
            'text': vault_options + "/3",
        }))

        if (vault_options == 1) {
            threshold_1_count++
        } else if (vault_options == 2) {
            threshold_2_count++
        } else if (vault_options == 3) {
            threshold_3_count++
        }
    })
    append_vault_summary(threshold_1_count, threshold_2_count, threshold_3_count)
}

function append_vault_summary(t1, t2, t3) {
    const MAX_VAULT_BOSSES_KILLED = 8
    const summary_div = $('<div/>', {
        class: 'great-vault-summary d-flex'
    })
    summary_div.append($('<div/>', {
        text: 'Summary'
    }))
    const rects = ($('<div/>', {
        class: 'rects d-flex'
    }))
    for (i = 0; i < MAX_VAULT_BOSSES_KILLED; i++) {
        let text = ""
        if (i == 1) {
            text = t1
        } else if (i == 4) {
            text = t2
        } else if (i == 7) {
            text = t3
        }
        rects.append($('<div/>', {
            'text': text,
            'class': "great-vault-boss-rect summary"
        }))
    }
    summary_div.append(rects)

    $('.summary-vault-info').append(summary_div)
}

function get_great_vault_list(roster_list) {
    let great_vault_list = []
    roster_list.forEach((char, index) => {
        great_vault_list.push({
            'char_name': char.name,
            'bosses_killed': get_vault_options_for_char(char.name, false)
        })
    })
    return great_vault_list
}

function get_vault_options_for_char(char_name, get_threshold = true) {
    count = 0
    for (let boss_id in boss_list_db_to_object(boss_list)) {
        if (is_char_selected_for_boss(boss_id, char_name)) {
            count++
        }
    }
    // Vault thresholds [ 2, 5, 8 ]
    if (get_threshold) {
        if (count >= 8) {
            return '3'
        } else if (count >= 5) {
            return '2'
        } else if (count >= 2) {
            return '1'
        } else {
            return '0'
        }
    }
    return count
}