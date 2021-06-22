var audio = document.querySelector("audio")
var control = document.getElementById("playlist-control")

function gotoNext() {
    let index = parseInt(control.getAttribute("index"))
    let mode = control.getAttribute("mode")
    let ntracks = control.getAttribute("ntracks")
    let shuffle = JSON.parse(control.getAttribute("shuffle"))

    if (mode == "play") {
        if (index + 1 <= ntracks) {
            gotoTrack(index + 1)
        }
    }

    if (mode == "repeat") {
        if (index + 1 <= ntracks) {
            gotoTrack(index + 1)
        } else {
            gotoTrack(1)
        }
    }

    if (mode == "shuffle") {
        gotoTrack(shuffle.pop())
    }
}


function gotoPrev() {
    let index = parseInt(control.getAttribute("index"))
    let mode = control.getAttribute("mode")
    let ntracks = control.getAttribute("ntracks")
    let shuffle = JSON.parse(control.getAttribute("shuffle"))

    if (mode == "play") {
        if (index - 1 > 0) {
            gotoTrack(index - 1)
        }
    }

    if (mode == "repeat") {
        if (index - 1 <= 0) {
            gotoTrack(ntracks)
        }
    }

    if (mode == "shuffle") {
        gotoTrack(shuffle.pop())
    }
}


function gotoRepeat() {
    location = "/repeat/" + control.getAttribute("name") + "/1"
}


function gotoShuffle() {
    location = "/shuffle/" + control.getAttribute("name")
}


function gotoTrack(num) {
    let name = control.getAttribute("name")
    let mode = control.getAttribute("mode")
    location = "/" + mode + "/" + name + "/" + num
}


function keyDown(e) {
    // console.log('keyDown: ' + e.code)
    if (e.code == "ArrowUp")    { e.preventDefault(); gotoPrev() }
    if (e.code == "ArrowRight") { e.preventDefault(); gotoNext() }
    if (e.code == "ArrowDown")  { e.preventDefault(); gotoNext() }
    if (e.code == "ArrowLeft")  { e.preventDefault(); gotoPrev() }
}

function keyPressed(e) {
    // console.log('keyPressed: ' + e.code)
    if (e.code == "KeyN") { e.preventDefault(); gotoNext() }
    if (e.code == "KeyP") { e.preventDefault(); gotoPrev() }
    if (e.code == "Space") { e.preventDefault(); playOrPause() }
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


if (audio) {
    audio.addEventListener("ended", gotoNext)
    document.addEventListener("keydown", keyDown)
    document.addEventListener("keypress", keyPressed)
}


function init() {
    console.log('playlist.js')
}
