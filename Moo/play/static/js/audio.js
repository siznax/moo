/** Moo **/

var DEBUG = false

var audio = document.querySelector("audio")
var control = document.getElementById('control')
var title = document.getElementById('title')

var smallBreakWidth = "640"


function adjustLayout() {
    let coverDiv = document.getElementById('album-cover')
    let audioDiv = document.getElementById('album-audio')

    if (window.innerWidth <= smallBreakWidth) {
        coverDiv.classList.add('small')
        audioDiv.classList.add('small')
    } else {
        coverDiv.classList.remove('small')
        audioDiv.classList.remove('small')
    }
}


function Bright() {
    let body = document.querySelector("body")
    body.classList.remove("dark")
}

function Dark() {
    let body = document.querySelector("body")
    body.classList.add("dark")
}



function gotoNext() {
    let next = control.getAttribute('next')
    if (next > 0) { 
        // title.classList.remove("glow")
        // track.classList.remove("glow")
        gotoTrack(next) 
    }
}

function gotoPrev() {
    let prev = control.getAttribute('prev')
    if (prev > 0) { 
        // title.classList.remove("glow")
        // track.classList.remove("glow")
        gotoTrack(prev) 
    }
}

function gotoRandom() {
    location = '/random'
}

function gotoRandomAlbum() {
    let ralbum = control.getAttribute("ralbum")
    let slash = ""
    if (ralbum[0] != "/") {
        slash = "/"
    }
    location = "/album" + slash + ralbum
}

function gotoTrack(num) {
    let ntracks = parseInt(control.getAttribute('ntracks'))
    if (parseInt(num) <= ntracks) {
        let alkey = control.getAttribute("alkey")
        location = "/track/" + num + "/" + alkey + "#" + num
    }
}

function hide(id) {
    elm = document.getElementById(id)
    elm.style.display = "none"
    elm.style.visibility = "hidden"
}

function init(version) {
    document.addEventListener("keydown", keyDown)
    document.addEventListener("keypress", keyPressed)

    if (audio) {
        adjustLayout()
        audio.addEventListener("ended", gotoNext)
        audio.focus({preventScroll:true})
    }

    window.onresize = adjustLayout

    console.log('Moo ' + version)
}

function keyDown(e) {

    // alert(e.keyCode)

    if (e.code == "ArrowUp") {
        e.preventDefault()
        gotoPrev() 
    }
    if (e.code == "ArrowRight") {
        e.preventDefault()
        gotoNext() 
    }
    if (e.code == "ArrowDown") {
        e.preventDefault()
        gotoNext() 
    }
    if (e.code == "ArrowLeft") {
        e.preventDefault()
        gotoPrev() 
    }
}

function keyPressed(e) {
   if (e.code == "KeyR") { gotoRandom() }
}


function playRandomTrack() {
    gotoTrack(control.getAttribute("rtrack"))
}


function toggle(id) {

    /* assumes element is initially visible */

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

    /* assumes element is initially hidden */

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

function show(id) {
    elm = document.getElementById(id)
    elm.style.display = "block"
    elm.style.visibility = "visible"
}
