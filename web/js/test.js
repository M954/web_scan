const data = `
[
    {
        "demo.aisec.cn":
            [
                {
                    "demo":
                    [
                        {
                            "aisec":
                            [
                                "html_link.php",
                                "js_link.php",
                                "post_link.php",
                                "click_link.php"
                            ]
                        }
                    ]
                }
            ]
    }
]`


// offset for each level
$('.structure p').each(function(index, el) {
    let level = $(el).parent().attr('class').split('level')[1];
    let offset = level * 10;
    $(this).css('margin-left', `${offset}px`);

});

// collapse for each level
$('.trigger-show').click(function(event) {
    $(this).hide();
    $(this).siblings('.trigger-hide').show();
    $(this).parent().siblings().show('fast');

});
$('.trigger-hide').click(function(event) {
    $(this).hide();
    $(this).siblings('.trigger-show').show();
    $(this).parent().siblings().hide('fast');
});



// test
$.ajax({
    url: '/momo/get_elements_from_db',
    dataType: 'json',
    // data: {searchWord: 'value1'}
})
.done(function(data) {
    console.log(data);
    console.log("success");
})
.fail(function() {
    console.log("error");
})
.always(function() {
    console.log("complete");
});
