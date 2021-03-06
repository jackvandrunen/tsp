// Global variables - only one set of cities and one tour can be displayed at one time

window.tspCities = []
window.tspTour = []
window.currentCity = -1

window.c = document.getElementById("mainCanvas")
window.ctx = c.getContext("2d")

var _array = new Uint32Array(1)
window.crypto.getRandomValues(_array)
window.clientId = _array[0]


// Utility functions

function distance(xy1, xy2)
{
    var dx = xy2[0] - xy1[0]
    var dy = xy2[1] - xy1[1]
    return Math.sqrt((dx * dx) + (dy * dy))
}

function drawCity(x, y, selected)
{
    var r = 5
    ctx.beginPath()
    ctx.arc(x, y, r, 0, 2 * Math.PI, false)
    ctx.fillStyle = (selected) ? "#00f" : "#f00"
    ctx.fill()
}

function drawEdge(a, b)
{
    var x1 = tspCities[a][0]
    var y1 = tspCities[a][1]
    var x2 = tspCities[b][0]
    var y2 = tspCities[b][1]

    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.strokeStyle = "#00f"
    ctx.lineWidth = 2
    ctx.stroke()
}

function drawCities()
{
    tspCities.forEach(function (xy) {
        drawCity(xy[0], xy[1])
    })
    if (currentCity >= 0)
    {
        drawCity(tspCities[currentCity][0], tspCities[currentCity][1], true)
    }
}

function drawEdges()
{
    var a = 0, b = 1
    for (; b < tspTour.length; a++, b++)
    {
        drawEdge(tspTour[a], tspTour[b])
    }
    if (tspTour.length > 0 && currentCity < 0) {
        drawEdge(tspTour[a], tspTour[0])
    }
}

function clearDrawing()
{
    ctx.fillStyle = "#fff"
    ctx.fillRect(0, 0, 500, 500)
}

function redraw()
{
    clearDrawing()
    drawEdges()
    drawCities()
}


// API functions

function clear()
{
    window.tspTour = []
    window.tspCities = []
}

function nextProblem()
{
    var xhr = new XMLHttpRequest()
    xhr.open("GET", "/api/" + window.problemIndex + "/cities", true)
    xhr.send(null)
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            clear()
            if (xhr.status == 200) {
                window.tspCities = JSON.parse(xhr.responseText)
                redraw()
            } else {
                window.alert("No more problems!")
            }
        }
    }
}

function recordTour()
{
    if (tspCities.length < 4) { return }
    var xhr = new XMLHttpRequest()
    xhr.open("POST", "/api/" + window.problemIndex + "/tour", true)
    xhr.send("data=" + encodeURIComponent(JSON.stringify(tspTour)))
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            window.problemIndex++
            nextProblem()
        }
    }
}


// UI functions

function getXY(ev)
{
    var rect = ev.target.getBoundingClientRect()
    var x = ev.clientX - rect.left
    var y = ev.clientY - rect.top
    return [x, y]
}

function restartTour(ev)
{
    window.tspTour = []
    redraw()
}

function sendTour(ev)
{
    if (tspTour.length != tspCities.length)
    {
        alert("Tour incomplete!")
        return
    }
    recordTour()
}

function buildTour()
{
    window.prevCity = -1
    return function(ev) {
        if (prevCity < 0 && tspTour.length > 0)
        {
            if (!confirm("Clear existing tour?"))
            {
                return
            }
            restartTour()
        }
        var xy = getXY(ev)
        var min = Infinity
        window.currentCity = -1
        for (var i = 0; i < tspCities.length; i++)
        {
            var dist = distance(xy, tspCities[i])
            if (dist < min)
            {
                min = dist
                window.currentCity = i
            }
        }
        if (tspTour.indexOf(currentCity) >= 0)
        {
            window.currentCity = prevCity
            return
        }
        tspTour.push(currentCity)
        if (tspTour.length < tspCities.length)
        {
            window.prevCity = currentCity
        }
        else
        {
            alert("Tour complete!")
            window.prevCity = -1
            window.currentCity = -1
        }
        redraw()
    }
}


window.c.onclick = buildTour()
document.getElementById("clearButton").onclick = restartTour
document.getElementById("submitButton").onclick = sendTour

window.problemIndex = 0
nextProblem()
