function fetchWeather() {
    if (window.fetch) {
        fetch("https://wttr.in/?format=%c")
            .then(response => response.text())
            .then(data => updateWeather(data))
    }
}


function updateTime() {
    let elm = document.getElementById('time')

    if (elm) {
        let time = new Date().toLocaleTimeString()
        let ampm = time.split(" ")[1]
        let hm_ = time.split(":", 2).join(":")
        elm.innerHTML = hm_ + " " + ampm
    }
}


function updateWeather(conditions) {
    let elm = document.getElementById('weather')

    if (elm) {
        elm.innerHTML = '<a href="https://wttr.in/" target="_blank">'
            + conditions + "</a>"
    }
}


fetchWeather()
setInterval(updateTime, 1000)
