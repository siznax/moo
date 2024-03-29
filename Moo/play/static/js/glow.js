function _addClass(obj, cls) {
    obj.classList.add(cls)
}

function _removeClass(obj, cls) {
    obj.classList.remove(cls)
}

function glowOn() {

    /* flicker for a bit */

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


var audio = document.querySelector("audio")

if (audio) {
    // audio.addEventListener("play", glowOn)
    // audio.addEventListener("pause", glowOff)
}
