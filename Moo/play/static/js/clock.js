function fetchWeather() {
    if (window.fetch) {
        fetch("https://wttr.in/?format=3")
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


function updateWeather(data) {
    let elm = document.getElementById("weather")

    if (data && elm) {
        let parts = data.split(" ")
        let icon = parts[parts.length - 2] || parts[parts.length - 3]
        elm.innerHTML = '<a href="https://wttr.in/" '
            + 'target="_blank" '
            + 'title="' + data.trim().replaceAll(" ", "\n") + '">'
            + icon + "</a>"
    }
}


fetchWeather()
setInterval(updateTime, 1000)
