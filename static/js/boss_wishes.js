function bossFieldsToObject(bossFields){
    let bosses = {}
    bossFields.forEach(boss => {
        bosses[boss.boss_id]={
            'name': boss.boss_name,
            'id':boss.boss_id,
        }
    })
    return bosses
}
function getQuerySetFields(querySet){
    let res = []
    querySet.forEach(e => {
        res.push(e.fields)
    });
    return res
}

function setListHeight(list){
    const amountOfChildren = $(list).children().length
    const LIST_ELEMENT_HEIGHT = parseInt($(list).find('.bosswish-boss').css('height'));
    const listCssPadding = parseInt($(list).css('padding-top') + $(list).css('padding-bottom'))
    $(list).height(LIST_ELEMENT_HEIGHT*amountOfChildren + listCssPadding)
}

function getBossWishFields(querySet){
    let fields = []
    querySet.forEach((wish)=>{
        fields.push(JSON.parse(wish)[0].fields)
    })
    return fields
}

function createBossWishDict(wishes){
    let res = {}
    wishes.forEach(wish=>{
        res[wish.character_id] = wish.wishes
    })
    return res
}

userChars = getQuerySetFields(userCharsDB)
bosses = bossFieldsToObject(getQuerySetFields(bossesDB))
wishes = getBossWishFields(bossWishes)
wishes = createBossWishDict(wishes)

class SortableList {
    constructor(listContainer, initialState) {
        this.listContainer = listContainer;
        this.userCharacterId = $(listContainer).attr('id')
        this.listElements = this.listElementsFromParent()
        this.orderedIdList = this.createOrderedIdList()
        if(initialState) this.loadDataFromDb(initialState) 
    }

    loadDataFromDb(initialState){
        for (const [id, val] of Object.entries(initialState)){
            const input = $(this.listContainer).find('#'+id).find('input')
            let inputVal = val
            if(val == '-') inputVal = 99
            $(input).val(inputVal)
            this.updateOrderedIdList(inputVal, id)   
        }
        this.updateDataOrderAttribute()
        this.updateInputValue()
    }

    listElementsFromParent(){
        return $(this.listContainer).children()
    }

    createOrderedIdList() {
        let ids = [];
        [...$(this.listContainer).children()].forEach((child)=>{
            ids.push(child.id)
        })
        return ids
    }

    updateOrderedIdList(userValue, bossId) {
        let wishValues = [];
        [...this.listElements].forEach((e)=>{
            wishValues.push($(e).find('input').val())
        })
        const arrayStartAtZeroOffset = 1
        let canHelpBosses = wishValues.filter(x => x==99).length
        let benchMeBosses = wishValues.filter(x => x==0).length
        let disabledBosses = canHelpBosses + benchMeBosses

        let newValue = clamp(userValue, 0, Object.keys(bosses).length - disabledBosses) - arrayStartAtZeroOffset
        if(userValue == 99)
            newValue = (Object.keys(bosses).length - 1) - benchMeBosses
        if(userValue == 0)
            newValue = Object.keys(bosses).length
        
        this.orderedIdList = this.moveItemInArray(this.orderedIdList, this.orderedIdList.indexOf(bossId), newValue)
    } 

    moveItemInArray(array, from, to, on = 1) {
        return array.splice(to, 0, ...array.splice(from, on)), array
    }

    setEventListeners() {
        [...this.listElements].forEach((element, index)=> {
            const input = $(element).find('input')
            $(input).on('focusout', ()=>{
                const bossId = element.id
                let userValue = $(input).val()
                if(userValue > 100){
                    $(input).val(99)
                    userValue = 99 }
                if(userValue < 0){
                    $(input).val(0)
                    userValue = 0 }
                
                
                this.updateOrderedIdList(userValue, bossId)
                this.updateDataOrderAttribute()
                this.updateInputValue()
                this.inputValueChanged()
            })
        })

        $('.save-wishes').on('click', ()=>{
            const btn = $('.save-wishes')
            btn.attr('loading',true)
            btn.addClass('ane-btn-disabled')
            setTimeout(()=>{
                btn.removeAttr('loading')
                status_alert(1500, "Wishes Saved", "success")
            },832)
            
            this.syncDataToDb()
        })

        this.setupDraggableListElements()
    }

    setupDraggableListElements() {
        /* 
        Makes the element of the list draggable to their correct position.
        */
        const AMOUNT_OF_BOSSES = Object.keys(bosses).length;
        const LIST_ELEMENT_HEIGHT = parseInt($(this.listContainer).find('.bosswish-boss').css('height'));
        [...this.listElements].forEach((element, index)=> {
            $(()=>{
                var elementStartY = 0
                var startDataOrder, mousePositionOffset
                var lastCalculatedDataOrder;
                const draggableIcon = $(element).find('.draggable-icon')
                $(draggableIcon).mousedown((event)=>{
                    startDataOrder = $(element).attr('data-order')
                    elementStartY = LIST_ELEMENT_HEIGHT * (startDataOrder - 1)
                    mousePositionOffset = elementStartY - getMouseYPosition(event) // Since mouseY 0 is not the top of the list we need to figure out the offset
                    $(element).attr('dragging', true) // The element will have an attribute so we know that it is currently being dragged
                })
                $(".bosswish-grid").mousemove((event)=>{ 
                    if($(element).attr('dragging')){
                        let elementPosition = getMouseYPosition(event) - Math.abs(mousePositionOffset)
                        $(element).css('top', clamp(elementPosition, 0, (AMOUNT_OF_BOSSES - 1) * LIST_ELEMENT_HEIGHT)) // Continously update the elements position while moving mouse (clamp within list boundaries)
                        console.log((AMOUNT_OF_BOSSES - 1) * LIST_ELEMENT_HEIGHT)
                        let value = calculateClosestDataOrderPosition(elementPosition)
                        if(lastCalculatedDataOrder != value){ // If the DataOrder changes then we know to move the other elements
                            $(element).attr('data-order', value)
                            $(element).find('input').val(value)
                            this.updateOrderedIdList(value, element.id)
                            this.updateDataOrderAttribute()
                            this.updateInputValue()
                        }
                        lastCalculatedDataOrder = calculateClosestDataOrderPosition(elementPosition)
                    }
                })
                $(".bosswish-grid").mouseup((event)=>{
                    if($(element).attr('dragging')){
                        let elementPosition = getMouseYPosition(event) - Math.abs(mousePositionOffset)
                        let value = calculateClosestDataOrderPosition(elementPosition)
                        $(element).attr('data-order', value)
                        $(element).css('top', "")
                        $(element).find('input').val(value)
                        this.updateOrderedIdList(value, element.id)
                        this.updateDataOrderAttribute()
                        this.updateInputValue()
                        this.inputValueChanged()
                    }
                    $(element).removeAttr('dragging')
                })
            })
        })

        function calculateClosestDataOrderPosition(elementPosition){
            return clamp(Math.round(elementPosition/LIST_ELEMENT_HEIGHT) + 1, 1, AMOUNT_OF_BOSSES)
        }
        function getMouseYPosition(event){
            var doc, body
            event = event || window.event
            event.pageX = event.clientX +
                (doc && doc.scrollLeft || body && body.scrollLeft || 0) -
                (doc && doc.clientLeft || body && body.clientLeft || 0);
            event.pageY = event.clientY +
                (doc && doc.scrollTop  || body && body.scrollTop  || 0) -
                (doc && doc.clientTop  || body && body.clientTop  || 0 );
            return event.pageY
        }
    }

    inputValueChanged() {
        const saveBtn = $('.save-wishes')
        saveBtn.removeClass('ane-btn-disabled')

    }

    updateDataOrderAttribute() {
        [...this.orderedIdList].forEach((id)=>{
            const listItem = $(this.listContainer).find('#'+id)
            let newIndex = this.orderedIdList.indexOf(id)
            $(listItem).attr('data-order', newIndex + 1)
        })
    }

    updateInputValue() {
        [...this.listElements].forEach((element, index)=> {
            const input = $(element).find('input')

            if($(input).val() == 99){
                $(element).addClass('can-help')
            } else if ($(input).val() <= 0) {
                $(element).addClass('bench-me')
            } else {
                $(element).removeClass('can-help bench-me')
                let newValue = this.orderedIdList.indexOf(element.id) + 1
                $(input).val(newValue)
            } 
        })
    }

    syncDataToDb(){
        // Fill wishes object with the bosses we have a value for
        let wishes = {};
        [...this.orderedIdList].forEach((id)=>{
            let val = $(this.listContainer).find("#"+id).find('input').val()
            wishes[id] = val
        })

        // Fill the rest of the entries with a '-'
        Object.entries(bosses).forEach((boss)=>{
            let id = parseInt(boss[0])
            if(!wishes[id]){
                wishes[id] = '-'
            }
        })

        $.ajax({
            url: window.location.href,
            data: {
                'wishes': JSON.stringify(wishes),
                'character_id': this.userCharacterId,
            },
            dataType: 'json',
            timeout: 1000,
        })
    }
}

// Initiate the class instances when the page has loaded \\
let sortableListObjects = []
$(document).ready(function(){
    const listElements = $('.draggable-list');
    [...listElements].forEach((element)=>{

        // If there are wishes saved in Db, load those. Else default to an empty list
        if(wishes[element.id]){
            let sortableList = new SortableList(element, wishes[element.id])
            sortableListObjects.push(sortableList)
        } else {
            let sortableList = new SortableList(element)
            sortableListObjects.push(sortableList)
        }

        // Set the height of the list to match the amount of elements
        setListHeight(element)
    })
    setTimeout(()=>{
        sortableListObjects.forEach((list)=>{
            initSortableList(list)
        })
    },100)
})

function initSortableList(list){
    list.setEventListeners()
    //list.updateOrderedIdList()
    setTimeout(()=> {
        list.updateDataOrderAttribute()
        list.updateInputValue()
    },50)
}


