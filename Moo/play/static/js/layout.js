var smallBreakWidth = "640"

function adjustLayout() {
    let coverDiv = document.getElementById('album-cover')
    let audioDiv = document.getElementById('album-audio')

    if (window.innerWidth <= smallBreakWidth) {
        coverDiv.classList.add('small')
        audioDiv.classList.add('small')
    } else {
        coverDiv.classList.remove('small')
        audioDiv.classList.remove('small')
    }
}

window.onload = adjustLayout
window.onresize = adjustLayout
