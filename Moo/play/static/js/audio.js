/** Moo **/

var DEBUG = false

var audio = document.querySelector("audio")
var control = document.getElementById('control')
var title = document.getElementById('title')

function _addClass(obj, cls) {
    obj.classList.add(cls)
}

function _removeClass(obj, cls) {
    obj.classList.remove(cls)
}

function gotoTrack(num) {
    let ntracks = parseInt(control.getAttribute('ntracks'))
    if (parseInt(num) <= ntracks) {
        let alkey = control.getAttribute("alkey")
        location = "/track/" + num + "/" + alkey + "#" + num
    }
}

function glowOn() {
    track.classList.add("glow")
    window.setTimeout(_removeClass, 150, track, "glow")
    window.setTimeout(_addClass, 250, track, "glow")

    title.classList.add("glow")
    window.setTimeout(_removeClass, 50, title, "glow")
    window.setTimeout(_addClass, 300, title, "glow")
}


function glowOff() {
    title.classList.remove("glow")
    track.classList.remove("glow")
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


function toggle(id) {  /* assumes element is initially visible */

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


function toggle_hidden(id) {  /* assumes element is initially hidden */

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


function zoomPlus() {
    alert(document.body.style.zoom)

    let scale = 'scale(1)'

    document.body.style.transform = scale

    document.body.style.msTransform = scale
    document.body.style.webkitTransform = scale
}



function init(version) {
    document.addEventListener("keydown", keyDown)
    document.addEventListener("keypress", keyPressed)

    let audio = document.querySelector("audio")
    if (audio) {
        // audio.addEventListener("play", glowOn)
        // audio.addEventListener("pause", glowOff)
        audio.addEventListener("ended", gotoNext)
        audio.focus({preventScroll:true})
    }

    console.log('Moo ' + version)
}
