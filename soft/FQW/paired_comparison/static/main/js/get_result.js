function getUserElem(id){
    userResultBlock = document.getElementById(id)
    modal = userResultBlock.parentNode
    return modal
}

function getUserResult(id){
    modal = getUserElem(id)
    modal.style.display = 'block'
}

function closeUserResult(id){
    modal = getUserElem(id)
    modal.style.display = 'none'
}