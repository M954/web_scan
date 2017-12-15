transToSearch = () => {
    $('#result').hide('400', () => {
        $('.search-wraper').show('400');
    });
    $('.backToSearch').hide();
}

transToResult = () => {
    $('.search-wraper').hide('400', () => {
        $('#result').show('400');
    });
    $('.backToSearch').show();
}
