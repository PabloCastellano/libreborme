// libreborme.net JS

function moreData(urlData, idPagePanel, idTable) {
    document.getElementById(idPagePanel).innerHTML = "Cargando...";
    AjaxRequest(urlData, function (res) {
        removeElementId(idPagePanel);
        $("#"+idTable).append(res.responseText);
    }, "post");
}

function removeElementId(elemId) {
    var elem = document.getElementById(elemId);
    if (elem) elem.parentNode.removeChild(elem);
}

// AJAX
function AjaxRequest(url, callback, method) {
    var req = new XMLHttpRequest();
    req.onreadystatechange = function () {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        callback(req);
    }
    req.open(method, url, true);
    var csrftoken = $.cookie('csrftoken');
    if (csrftoken) req.setRequestHeader("X-CSRFToken", csrftoken);
    req.send(null);
}
