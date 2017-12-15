addItemToTable = (id, name, description, time) => {
    let td_id = $(`<td>${id}</td>`);
    let td_name = $(`<td>${name}</td>`);
    let td_description = $(`<td>${description}</td>`);
    let td_time = $(`<td>${time}</td>`);
    let tr = $('<tr></tr>').append(td_id, td_name, td_description, td_time);
    $('#table > tbody').append(tr);
}

addItemToTable(10, 'test', 'hahaha', '3 minute ago');

getItemFromDB = () => {
    console.log('todo');
}
