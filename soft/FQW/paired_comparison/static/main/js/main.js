comparisonBlock = document.querySelector('#comparison')
targetsBlock = document.querySelector('#targets')
infoBlock = document.querySelector('#info')

async function setAndGetData(source){
    url =  window.location.href +'/get_targets'
    if (!source.window){
        targetsButtons = targetsBlock.children
        result = {}
        if (source.id == 'draw'){
            result.draw = 'true'
            result.winner = targetsButtons[0].id
            result.loser = targetsButtons[1].id
        }else{
            for (targetsButton of targetsButtons){
                if (targetsButton.id == source.id){
                result.winner = targetsButton.id
                }else if (targetsButton.id != 'draw'){
                   result.loser = targetsButton.id
                }
        }}
        console.log('Отправлен результат:',result)
        targets = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(result)
        })
    }else{
        targets = await fetch(url)
    }
    json = await targets.json()
    console.log('Получены данные:', json)
    return json
}

function getCookie(str){
    cookies = document.cookie.split('; ')
    for (cookie of cookies){
        if (cookie.includes(str)){
            cookie = cookie.split('=').pop()
            return cookie
        }
    }
}


function createInfoBlock(info){
    title = document.createElement('h2')
    text = document.createTextNode(info.title)
    title.append(text)
    infoBlock.append(title)
    ask = document.createElement('i')
    ask.addEventListener('click', () => getUserResult('what-do'))
    text = document.createTextNode('🖝 Что делать?')
    ask.append(text)
    infoBlock.append(ask)
    if (info.description != ''){
        description = document.createElement('details')
        summary = document.createElement('summary')
        text = document.createTextNode('Подробнее')
        summary.append(text)
        description.append(summary)
        text = document.createTextNode(info.description)
        description.append(text)
        infoBlock.append(description)
    }
    console.log('Создан блок информации: ' + info.id + '. ' + info.title)
}

function createErrorBlock(errors){
    div = document.createElement('div')
    div.classList.add('error')
    ul = document.createElement('ul')
    for (error of errors){
        li = document.createElement('li')
        text = document.createTextNode(error)
        li.append(text)
        ul.append(li)
    }
    div.append(ul)
    targetsBlock.before(div)
}

function createButton(target, info){
        targetButton = document.createElement('div')
        if (target){
            targetButton.id = target.id
            text = document.createTextNode(target.title)
        } else{
            targetButton.id = 'draw'
            text = document.createTextNode('Прорустить')
        }
        targetButton.onclick = createComparisonBlock
        title = document.createElement('b')
        title.append(text)
        targetButton.append(title)
        if (target && info){
            ul = document.createElement('ul')
            for (i = 0; i < target.parameters.length; i++){
                li = document.createElement('li')
                text = document.createTextNode(info.parameters_title[i])
                br = document.createElement('br')
                li.append(text, br)
                text = document.createTextNode(target.parameters[i])
                li.append(text)
                ul.append(li)
            }
            targetButton.append(ul)
        }
        targetsBlock.append(targetButton)
}

function createButtons(targets, info){
    while (targetsBlock.childElementCount > 0){
        targetsBlock.lastChild.remove()
    }
    if (json.errors){
        createErrorBlock(json.errors)
    }

    for (target of targets){
        createButton(target, info)
    }
    createButton()
}

async function createComparisonBlock(){
    json = await setAndGetData(this)
    if (json.new_user) {
        location.href = `${location.href}/create_user`
    }
    if (infoBlock.childElementCount == 0){
        createInfoBlock(json.comparison)
    }
    createButtons(json.targets, json.comparison)
}

comparisonBlock.onload = createComparisonBlock()