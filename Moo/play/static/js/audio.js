/** Moo **/

var DEBUG = false

var audio = document.querySelector("audio")
var control = document.getElementById('control')
var title = document.getElementById('title')

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
    if (audio) {
        adjustLayout()
        audio.addEventListener("ended", gotoNext)
    }
    window.onresize = adjustLayout
    console.log('Moo ' + version)
}


function playOrPause() {
    if (audio) {
        if (audio.paused) {
            audio.play()
        } else {
            audio.pause()
        }
    }
}


function playRandomTrack() {
    gotoTrack(control.getAttribute("rtrack"))
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
