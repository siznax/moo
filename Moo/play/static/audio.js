/** Moo **/

var DEBUG = false

var audio = document.querySelector("audio")
var clock = document.getElementById('clock')
var control = document.getElementById('control')
var title = document.getElementById('title')
var track = document.getElementById('track')


function _addClass(obj, cls) {
    obj.classList.add(cls)
}

function _removeClass(obj, cls) {
    obj.classList.remove(cls)
}

function blurgray(sel) {
    let elm = document.querySelector(sel)
    elm.style.filter = "blur(8px) grayscale(1)"
}


function blurgray_clear(sel) {
    let elm = document.querySelector(sel)
    elm.style.filter = "blur(0) grayscale(0)"
}

function dark() {
    let body = document.getElementById("body")
    body.classList.toggle("dark")
}

function gotoCovers() {
    window.location = "/covers"
}

function gotoTrack(num) {
    let ntracks = parseInt(control.getAttribute('ntracks'))
    if (parseInt(num) <= ntracks) {
        let alkey = track.getAttribute("alkey")
        location = "/track/" + num + "/" + alkey
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


function gotoIndex() {
    window.location = "/"
}


function gotoNext() {
    let next = control.getAttribute('next')
    if (next > 0) { 
        title.classList.remove("glow")
        track.classList.remove("glow")
        gotoTrack(next) 
    }
}


function gotoPrev() {
    let prev = control.getAttribute('prev')
    if (prev > 0) { 
        title.classList.remove("glow")
        track.classList.remove("glow")
        gotoTrack(prev) 
    }
}


function gotoRandom() {
    location = '/random'
}


function hide(sel) {
    elm = document.querySelectorAll(sel)
    elm.forEach(function(obj) {
        obj.style.visibility = "hidden"
    })
}


// function hideOtherOverlays(not_id) {
//     ols = document.querySelectorAll('.overlay')
//     ols.forEach(function(item) { 
//         if (item.id != 'not_id') { 
//             item.style.display = 'none' 
//         }
//     })
// }


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

    // alert(e.code)

    if (e.code == "Space") {
        e.preventDefault()
        if (audio.paused) { 
            audio.play() 
            glowOn()
        }
        else { 
            audio.pause() 
            glowOff()
        }
    } 

    else if (e.code == "KeyN") { gotoNext() }
    else if (e.code == "KeyP") { gotoPrev() }
    else if (e.code == "KeyR") { gotoRandom() }
    else if (e.code == "KeyT") { playRandomTrack() }

    else if (e.code == "KeyC") { toggle_hidden('covers') }
    else if (e.code == "KeyD") { toggle_hidden("metadata") }
    else if (e.code == "KeyG") { toggle_hidden("tags") }
    else if (e.code == "KeyH") { toggle_hidden("help") }
    else if (e.code == "KeyI") { toggle_hidden('index') }
    else if (e.code == "KeyL") { toggle_hidden("classical") }
    else if (e.code == "KeyM") { toggle_hidden("related") }

    else if (e.code == "Digit1") { gotoTrack(1) }
    else if (e.code == "Digit2") { gotoTrack(2) }
    else if (e.code == "Digit3") { gotoTrack(3) }
    else if (e.code == "Digit4") { gotoTrack(4) }
    else if (e.code == "Digit5") { gotoTrack(5) }
    else if (e.code == "Digit6") { gotoTrack(6) }
    else if (e.code == "Digit7") { gotoTrack(7) }
    else if (e.code == "Digit8") { gotoTrack(8) }
    else if (e.code == "Digit9") { gotoTrack(9) }
    else if (e.code == "Digit0") { gotoTrack(10) }

    else {
    }
}


function playRandomTrack() {
    let rtrack = track.getAttribute("rtrack")
    gotoTrack(rtrack)
}


function toggle(id) {  /* assumes element is initially visible */
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


// toggle_overlay(id) assumes element is initially NOT visible
//
function toggle_overlay(id) {

    if (DEBUG) { console.log("toggle_overlay('" + id + "')") }

    let elm = document.getElementById(id)
    let disp = elm.style.display
    let type = elm.tagName

    // hideOtherOverlays(id)

    if (!disp) {
        // blurgray('img#cover')
        if (type == 'table') {
            elm.style.display = 'table'
        } else {
            elm.style.display = 'block'
        }
    } else if (disp === 'none') {
        // blurgray('img#cover')
        if (type == 'table') {
            elm.style.display = 'table'
        } else {
            elm.style.display = 'block'
        }
    } else if (disp = 'block') {
        // blurgray_clear('img#cover')
        elm.style.display = 'none'
    } else {
        // blurgray_clear('img#cover')
        elm.style.display = 'none'
    }

    if (DEBUG) {
        console.log("'" + disp + "' => " + elm.style.display)
    }
}


function updateClock() {
    if (clock) {
        let time = new Date().toLocaleTimeString()
        let ampm = time.split(" ")[1]
        let hm_ = time.split(":", 2).join(":")
        clock.innerHTML = hm_ + " <smcap>" + ampm + "</smcap>"
    }
}


function init(version) {
    document.addEventListener("keydown", keyDown)
    document.addEventListener("keypress", keyPressed)

    let audio = document.querySelector("audio")
    if (audio) {
        audio.addEventListener("play", glowOn)
        audio.addEventListener("pause", glowOff)
        audio.addEventListener("ended", gotoNext)
    }

    // let navigator = document.getElementById('navigator')
    // let nav = window.navigator
    // console.log(nav)
    // navigator.innerHTML = nav.userAgent
    // console.log(nav.userAgent)

    setInterval(updateClock, 1000)

    console.log('Moo ' + version)
}
