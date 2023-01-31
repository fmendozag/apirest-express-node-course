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

function validarCedula(cedula) {
    var cad = cedula.trim();
    var total = 0;
    var longitud = cad.length;
    var longcheck = longitud - 1;

    if (cad !== "" && longitud === 10) {
        for (i = 0; i < longcheck; i++) {
            if (i % 2 === 0) {
                var aux = cad.charAt(i) * 2;
                if (aux > 9) aux -= 9;
                total += aux;
            } else {
                total += parseInt(cad.charAt(i)); // parseInt o concatenará en lugar de sumar
            }
        }
        total = total % 10 ? 10 - total % 10 : 0;
        return cad.charAt(longitud - 1) == total? true:false;
    }
    return false;
}

