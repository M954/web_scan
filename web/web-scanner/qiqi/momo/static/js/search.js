$('.search-btn').click(function(event) {
    let input = $('#search-text').val();
    console.log(input);
    $.ajax({
        method: 'GET',
        url: `/momo/start_scan?url=${escape(input)}`,
        // dataType: 'json',
        // data: {searchWord: 'value1'}
    })
    .done(function(data) {
        console.log(data);
        console.log("success");
        return data;
    })
    .fail(function() {
        console.log("error");
    })
    .always(function() {
        console.log("complete");
    });
    transToResult();
});

$('#search-text').bind("enterKey",function(e){
    let input = $('#search-text').val();
    transToResult();
});
$('#search-text').keyup(function(e){
    if(e.keyCode == 13)
    {
        $(this).trigger("enterKey");
    }
});
