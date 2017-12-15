addItemToTable = (id, name, description, time) => {
    let td_id = $(`<td>${id}</td>`);
    let td_name = $(`<td>${name}</td>`);
    let td_description = $(`<td>${description}</td>`);
    let td_more = $(`<td><i class="fa fa-search trigger-search"></i></td>`);
    set_more($(td_more).children("i"));
    let tr = $('<tr></tr>').append(td_id, td_name, td_description, td_more);
    $('#table > tbody').append(tr);
}

addItemToTable(10, 'test', 'hahaha', '3 minute ago');

getItemFromDB = () => {
    console.log('todo');
}
