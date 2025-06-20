jQuery(document).ready(function($) {
    $('.wcdpc-field').on('change', function() {
        let selections = {};
        $('.wcdpc-field').each(function() {
            let key = $(this).data('name');
            let val = $(this).val();
            selections[key] = val;
        });

        $.post(wcdpc_ajax.url, {
            action: 'wcdpc_get_price',
            product_id: $('input[name="product_id"]').val(),
            selections: selections
        }, function(response) {
            let data = JSON.parse(response);
            if (data.price) {
                $('#wcdpc-price').text('€' + data.price.toFixed(2));
            }
        });
    });
});
