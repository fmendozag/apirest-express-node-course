(function ($) {
    'use strict';

    $(document).ready(function () {

        $('#id_rentabilidad_costo_contado').on('change blur', function (e) {
            let valor = Number($(this).val()) || 0;
            let costo_compra = Number($('#id_costo_compra').val()) || 0;
            let precio = Math.round((costo_compra + (costo_compra * (valor/100)))* 10000 + Number.EPSILON)/10000;
            $('#id_web_precio_contado').val(Number(precio));
        });

        $('#id_rentabilidad_costo_credito').on('change blur', function (e) {
            let valor = Number($(this).val()) || 0;
            let costo_compra = Number($('#id_costo_compra').val()) || 0;
            let precio = Math.round((costo_compra + (costo_compra * (valor/100)))* 10000 + Number.EPSILON)/10000;
            $('#id_web_precio_credito').val(Number(precio));
        });


        $('#id_comision_pvp_contado').on('change blur', function (e) {
            let valor = Number($(this).val()) || 0;
            let precio_contado = Number($('#id_web_precio_contado').val()) || 0;
            let comision_contado = Math.round((precio_contado * (valor/100))* 100 + Number.EPSILON)/100;
            $('#id_web_comision_contado').val(Number(comision_contado));
        });

        $('#id_comision_pvp_credito').on('change blur', function (e) {
            let valor = Number($(this).val()) || 0;
            let precio_credito = Number($('#id_web_precio_credito').val()) || 0;
            let comision_credito = Math.round((precio_credito * (valor/100))* 100 + Number.EPSILON)/100;
            $('#id_web_comision_credito').val(Number(comision_credito));
        });



    });

})(django.jQuery);

