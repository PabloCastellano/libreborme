$( function() {

    $( "#id_company" ).autocomplete({
        source: "/alertas/suggest_company",
        type: "post",
        minLength: 2,
        select: function( event, ui ) {
            $( "#id_company" ).val(ui.item.id );
            return false;
        }
    });

    $( "#id_person" ).autocomplete({
        source: "/alertas/suggest_person",
        type: "post",
        minLength: 2,
        select: function( event, ui ) {
            $( "#id_person" ).val(ui.item.id );
            return false;
        }
    });

} );