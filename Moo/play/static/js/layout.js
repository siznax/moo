/** Moo **/

var DEBUG = false

var smallBreakWidth = "640"
var thinBreakHeight = "320"


function Bright() {
    let body = document.querySelector("body")
    body.classList.remove("dark")
}


function Dark() {
    let body = document.querySelector("body")
    body.classList.add("dark")
}


function adjustLayout() {
    let coverDiv = document.getElementById('album-cover')
    let audioDiv = document.getElementById('album-audio')

    if (!coverDiv || !audioDiv) { return true }

    if (window.innerWidth <= smallBreakWidth) {
        coverDiv.classList.add('small')
        audioDiv.classList.add('small')
    } else if (window.innerHeight <= thinBreakHeight) {
        coverDiv.classList.add('thin')
        audioDiv.classList.add('thin')
    } else {
        audioDiv.classList.remove('small')
        audioDiv.classList.remove('thin')
        coverDiv.classList.remove('small')
        coverDiv.classList.remove('thin')
    }
}


function hide(id) {
    elm = document.getElementById(id)
    elm.style.display = "none"
    elm.style.visibility = "hidden"
}


function show(id) {
    elm = document.getElementById(id)
    elm.style.display = "block"
    elm.style.visibility = "visible"
}

function toggle(id) {

    // assumes element is initially visible

    event.preventDefault()

    let btn = event.target
    let elm = document.getElementById(id)
    let type = elm.tagName
    
    if (!elm.style.display) {
        elm.style.display = "none"
    } else if (elm.style.display == "block") {
        elm.style.display = "none"
    } else if (elm.style.display == "table") {
        elm.style.display = "none"
    } else {
        if (type == 'TABLE') {
            elm.style.display = "table"
        } else {
            elm.style.display = "block"
        }
    }

}


function toggle_hidden(id) {

    // assumes element is initially hidden

    event.preventDefault()

    let btn = event.target
    let elm = document.getElementById(id)
    let cover = document.getElementById("cover_img")
    let type = elm.tagName

    if (!elm.style.display) {
        if (type == 'TABLE') {
            elm.style.display = "table"
        } else {
            elm.style.display = "block"
        }
    } else if (elm.style.display == "none") {
        if (type == 'TABLE') {
            elm.style.display = "table"
        } else {
            elm.style.display = "block"
        }
    } else {
        elm.style.display = "none"
    }

}


adjustLayout()
window.onresize = adjustLayout

console.log('Moo')

