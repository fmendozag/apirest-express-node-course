function numerico(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode != 8 && keyCode != 0 && keyCode != 46 && keyCode != 13 && keyCode != 9 && (keyCode < 48 || keyCode > 57)) {
        return false;
    }
    if (e.target.value.indexOf('.') >= 0 && keyCode == 46) {
        return false;
    }
    return true;
};
