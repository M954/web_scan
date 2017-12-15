const pageBefore = $('<div class="before page">&lt;-</div>');
const pageAfter = $('<div class="next page">-&gt;</div>');
const paginator = $('#paginator');

initPaginator = (num) => {
    paginator.empty();
    paginator.append(pageBefore);
    for (var i = 0; i < num; i++) {
        let page = $(`<div class="page">${i+1}</div>`);
        paginator.append(page);
    }
    paginator.append(pageAfter);
    $('.page:nth-child(2)').addClass('curPage');
}

initPaginator(5);
