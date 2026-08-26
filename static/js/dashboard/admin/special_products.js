function search_products() {
    $('#product-select').select2({
        placeholder: 'Search Product',
        minimumInputLength: 2,

        ajax: {
            url: searchProductUrl,
            dataType: 'json',
            delay: 500,

            data: function (params) {
                return {
                    q: params.term
                };
            },

            processResults: function (data) {
                return {
                    results: data
                };
            }
        }
    });

    $('#product-select').on('select2:select', function (e) {
        var data = e.params.data;
        if ($('#product-select option[value="' + data.id + '"]').length === 0) {
            var newOption = new Option(data.text, data.id, true, true);
            $('#product-select').append(newOption).trigger('change');
        }
    });
}

$(document).ready(function () {
    search_products();
});