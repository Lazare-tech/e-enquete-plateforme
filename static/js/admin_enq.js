(function($) {
    'use strict';

    function toggleFields(row) {
        // On cherche le select du type
        const typeSelect = row.find('.field-question_type select');
        // On cherche le conteneur de la description
        const helpTextRow = row.find('.field-help_text');

        if (typeSelect.length && helpTextRow.length) {
            const val = typeSelect.val();
            console.log("Type détecté :", val); // Debug

            if (val === 'section' ) {
                helpTextRow.show();
            } else {
                helpTextRow.hide();
            }
        }
    }

    $(document).ready(function() {
        console.log("Script admin_enq.js chargé !");

        // Appliquer sur les lignes existantes
        $('.inline-related').each(function() {
            toggleFields($(this));
        });

        // Appliquer lors d'un changement
        $(document).on('change', 'select[name$="question_type"]', function() {
            const row = $(this).closest('.inline-related');
            toggleFields(row);
        });

        // Appliquer lors de l'ajout d'une nouvelle ligne
        $(document).on('formset:added', function(event, $row) {
            toggleFields($row);
        });
    });
})(django.jQuery || jQuery);