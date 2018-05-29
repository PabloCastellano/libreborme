// libreborme.net JS

function toggle_positions() {
    var e = document.getElementById('positions_history');
    if (e.style.display == 'none'){
        e.style.display = 'block';
        document.getElementById('toggle_positions_on').style.display = 'none';
        document.getElementById('toggle_positions_off').style.display = 'block';
    } else {
        e.style.display = 'none';
        document.getElementById('toggle_positions_on').style.display = 'block';
        document.getElementById('toggle_positions_off').style.display = 'none';
    }
    return true;
}

function moreData(urlData, idPagePanel, idTable) {
    document.getElementById(idPagePanel).innerHTML = "Cargando...";
    AjaxRequest(urlData, function (res) {
        removeElementId(idPagePanel);
        $("#"+idTable).append(res.responseText);
    }, "post", null);
}

function removeElementId(elemId) {
    var elem = document.getElementById(elemId);
    if (elem) elem.parentNode.removeChild(elem);
}

// AJAX
function AjaxRequest(url, callback, method, params) {
    var req = new XMLHttpRequest();
    req.onreadystatechange = function () {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        callback(req);
    }
    req.open(method, url, true);
    var csrftoken = $.cookie('csrftoken');
    if (csrftoken) req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send(params);
}
