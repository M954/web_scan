$('.search-btn').click(function(event) {
    let input = $('#search-text').val();
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
