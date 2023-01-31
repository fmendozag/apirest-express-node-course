function form_send(
            frmAction,//url the form has to be sended to
            frmMethod,//post||get
            winName,//name used for window and form-target
            winOpts,//options for window.open
            jsonName,//the name of the json inside _POST
            json//the object to send
) {
    //open the window
    var win = window.open("", winName, winOpts);
    win.blur();
    //create form & input and append it to the body
    var f = document.createElement('form');
    f.setAttribute('action', frmAction);
    f.style.display = 'none';
    f.target = winName;
    f.setAttribute('method', frmMethod);

    var e = document.createElement('input');
    e.setAttribute('name', jsonName);
    e.setAttribute('value', JSON.stringify(json));
    f.appendChild(e);

    var token = document.createElement('input');
    token.setAttribute('name', 'csrfmiddlewaretoken');
    token.setAttribute('value', csrftoken);
    f.appendChild(token);

    document.body.appendChild(f);
    //send the form
    f.submit();
    //remove the form after a moment
    setTimeout(function () {
        f.parentNode.removeChild(f);
    }, 50);
    return false;
}
