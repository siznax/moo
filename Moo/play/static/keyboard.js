function keyPressed(e) {

    // alert(e.code)

    if (e.code == "Space") {
        e.preventDefault()
        if (audio.paused) { 
            audio.play() 
            // glowOn()
        }
        else { 
            audio.pause() 
            // glowOff()
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
        // ignore
    }
}


document.addEventListener("keypress", keyPressed)
