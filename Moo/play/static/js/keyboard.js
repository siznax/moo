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

    else {
        // ignore
    }
}


document.addEventListener("keydown", keyDown)
document.addEventListener("keypress", keyPressed)
