window.tspCities = []
window.tspTour = []
window.tourTimes = []

window.problemIndex = 0
window.tourComplete = false
window.setCompleted = false

window.cHeight = 500
window.cWidth = 500
window.c = document.getElementById("mainCanvas")
window.ctx = c.getContext("2d")

var _array = new Uint32Array(1)
window.crypto.getRandomValues(_array)
window.clientId = _array[0]


var MAX_DISTANCE = 16


// Utility functions

function checkComplete()
{
    return tspTour.length == tspCities.length - 1
}

function distance(xy1, xy2)
{
    var dx = xy2[0] - xy1[0]
    var dy = xy2[1] - xy1[1]
    return Math.sqrt((dx * dx) + (dy * dy))
}


var CURRENT = "#000"
var COLORS = ["#00f", "#f90"]

function drawVertex(x, y, color)
{
    var r = 5
    ctx.beginPath()
    ctx.arc(x, y, r, 0, 2 * Math.PI, false)
    ctx.fillStyle = color
    ctx.fill()
}

function drawEdge(xy1, xy2, color, thickness)
{
    var x1 = xy1[0]
    var y1 = xy1[1]
    var x2 = xy2[0]
    var y2 = xy2[1]

    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.strokeStyle = color
    ctx.lineWidth = thickness
    ctx.stroke()
}

function drawCities()
{
    tspCities.forEach(function (xyc) {
        drawVertex(xyc[0], xyc[1], xyc[2])
    })
}

function drawTour()
{
    for (var i = 0; i < tspTour.length - 1; i++)
    {
        var xy1 = tspCities[tspTour[i]]
        var xy2 = tspCities[tspTour[i + 1]]
        drawEdge(xy1, xy2, "#000", 2)
    }
}

function clearDrawing()
{
    ctx.fillStyle = "#fff"
    ctx.fillRect(0, 0, cHeight, cWidth)
}

function resize()
{
    c.height = cHeight * 2
    c.width = cWidth * 2
    window.ctx = c.getContext("2d")
    ctx.scale(2, 2)
}

function redraw()
{
    clearDrawing()
    resize()
    drawCities()
    drawTour()
}


// API functions

function clear()
{
    window.tspCities = []
    window.tspTour = []
    window.tourTimes = []
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
                var response = JSON.parse(xhr.responseText)
                window.tspCities = response.cities
                for (var i = 0; i < tspCities.length; i++)
                {
                    window.tspCities[i] = [tspCities[i][0], tspCities[i][1], response.colors[i]]
                }
                window.cHeight = response.height
                window.cWidth = response.width
                redraw()
                document.getElementById("bottomBar").innerText = "Problem " + (window.problemIndex + 1)
            } else {
                window.setCompleted = true
                window.alert("No more problems!")
            }
        }
    }
}

function recordTour()
{
    var xhr = new XMLHttpRequest()
    xhr.open("POST", "/api/" + window.problemIndex + "/tour", true)
    xhr.send("data=" + encodeURIComponent(JSON.stringify([tspTour, tourTimes])))
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
    x = x * cWidth / c.width
    y = y * cHeight / c.height
    return [x, y]
}

function restartTour(ev)
{
    if (!confirm("Clear existing tour?"))
        return
    window.tspTour = []
    window.tourTimes = []
    window.tourComplete = false
    redraw()
}

function undoTour(ev)
{
    if (tspTour.length === 0)
        return
    tspTour.pop()
    if (tspTour.length > 1)
        tourTimes.pop()
    window.tourComplete = false
}

function sendTour(ev)
{
    if (!tourComplete)
    {
        alert("Tour incomplete!")
        return
    }
    recordTour()
    window.tourComplete = false
}

function buildTour(ev)
{
    if (tourComplete)
    {
        restartTour()
    }
    var xy = getXY(ev)
    var min = Infinity
    var nextCity = null
    for (var i = 0; i < tspCities.length; i++)
    {
        if (tspTour.includes(i))
            continue
        var dist = distance(xy, tspCities[i])
        if (dist < min)
        {
            min = dist
            nextCity = tspCities[i]
        }
    }
    if (min > MAX_DISTANCE)
        nextCity = null
    if (nextCity === null)
    {
        // alert("No active vertices!")
        return
    }
    tourTimes.push(new Date().getTime())
    tspTour.push(nextCity)
    if (checkComplete())
    {
        window.tourComplete = true
        redraw()
        setTimeout(function(){ alert("Tour complete!"); }, 100);
    }
}

function cancelReload(ev)
{
    return setCompleted
}

window.c.onclick = buildTour
window.onbeforeunload = cancelReload
document.getElementById("clearButton").onclick = restartTour
document.getElementById("undoButton").onclick = undoTour
document.getElementById("submitButton").onclick = sendTour
nextProblem()
