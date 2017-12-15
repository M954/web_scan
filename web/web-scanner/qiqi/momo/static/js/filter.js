
filter_flag = {
    'SQL injection':'off',
    'XSS':'off',
    'Senstive file':'off',
    'File inclusion':'off',
    'all':'off',
}

$(".filter1").click(function(event) {
    console.log($(this).text());
    let type = $(this).text();
    console.log(filter_flag[type]);
    myrefresh_bugs(type);
    // if(filter_flag[type] == 'on') {
    //     filter_flag[type] = 'off';
    //     myrefresh_bugs('all');
    // }else {
    //     // console.log('now is off');
    //     filter_flag[type] = 'on';
        // $("tbody tr").each(function(index, el) {
        //     console.log($(this).find('td:eq(1)').text());
    //         let childtext = $(this).find('td:eq(1)').text();
    //         if(childtext != type) {
    //             $(this).remove();
    //         }
    //     });
    // }
    // console.log('show');
    // $(this).hide();
    // $(this).siblings('.trigger-hide').show();
    // $(this).parent().siblings().show('fast');
});
