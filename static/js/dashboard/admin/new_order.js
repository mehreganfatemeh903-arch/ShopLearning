function addOrderItem() {}

function search_customer() {
    $('#customer-name').select2({
        placeholder: 'Search Customer',
        minimumInputLength: 2,
        cache: true,
        ajax: {
            url: searchCustomerUrl,
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
}

function search_product() {}

$(document).ready(function () {
    search_customer();
    search_product();
});