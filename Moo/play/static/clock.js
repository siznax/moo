var time_elm = document.getElementById('time')

function updateTime() {
    if (time_elm) {
        let time = new Date().toLocaleTimeString()
        let ampm = time.split(" ")[1]
        let hm_ = time.split(":", 2).join(":")
        time_elm.innerHTML = hm_ + " " + ampm
    }
}

setInterval(updateTime, 1000)
