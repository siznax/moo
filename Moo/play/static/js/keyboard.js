var audio = document.querySelector("audio")
var control = document.getElementById('control')


function gotoNext() {
    let next = control.getAttribute('next')
    if (next > 0) {
        gotoTrack(next)
    }
}


function gotoPrev() {
    let prev = control.getAttribute('prev')
    if (prev > 0) {
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
        location = "/track/" + num + "/" + alkey  // + "#" + num
    }
}


function keyDown(e) {
    if (e.code == "ArrowUp") { e.preventDefault(); gotoPrev() }
    if (e.code == "ArrowRight") { e.preventDefault(); gotoNext() }
    if (e.code == "ArrowDown") { e.preventDefault(); gotoNext() }
    if (e.code == "ArrowLeft") { e.preventDefault(); gotoPrev() }
}


function keyPressed(e) {
    console.log('keyPressed: ' + e.code)
    if (e.code == "KeyN") { gotoNext() }
    else if (e.code == "KeyP") { gotoPrev() }
    else if (e.code == "KeyR") { gotoRandom() }
    else if (e.code == "KeyT") { playRandomTrack() }
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
    else if (e.code == "Space") { e.preventDefault(); playOrPause() }
    else {}
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


if (audio) {
    audio.addEventListener("ended", gotoNext)
}


document.addEventListener("keydown", keyDown)
document.addEventListener("keypress", keyPressed)
