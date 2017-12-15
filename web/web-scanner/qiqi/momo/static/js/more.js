
function get_more(type, url) {
    $.ajax({
        url: `/momo/get_more_from_db?type=${type}&url=${escape(url)}`,
        dataType: 'json',
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
}

function check_hide(el_tr){
    el_next = $(el_tr).next();
    next_class = $(el_next).attr('class');
    if(next_class == 'info') {
        $(el_next).remove();
        return true;
    }else{
        return false;
    }
}

function addinfo_sql(data, tr_parent) {
    let dbms = $(`<div align="left">dbms : ${data.dbms}</div>`);
    let dbms_version = $(`<div align="left">dbms_version : ${data.dbms_version}</div>`);
    let payload = $(`<div align="left">payload : ${data.data}</div>`);
    let td = $('<td colspan="4"></td>').append(dbms, dbms_version, payload);
    let tr = $('<tr class="info"></tr>').append(td);
    // console.log($(that).get(0).tagName);
    $(tr_parent).after(tr);
}

function addinfo_xss(data, tr_parent) {
    let payload = $(`<div align="left">payload : ${data.payload}</div>`);
    let td = $('<td colspan="4"></td>').append(payload);
    let tr = $('<tr class="info"></tr>').append(td);
    // console.log($(that).get(0).tagName);
    $(tr_parent).after(tr);
}

function addinfo_file(data, tr_parent) {
    let domain = $(`<div align="left">domain : ${data.domain}</div>`);
    let url = $(`<div align="left">url : ${data.url}</div>`);
    let status = $(`<div align="left">status : ${data.status}</div>`);
    let td = $('<td colspan="4"></td>').append(domain, url, status);
    let tr = $('<tr class="info"></tr>').append(td);
    // console.log($(that).get(0).tagName);
    $(tr_parent).after(tr);
}

function addinfo_lfi(data, tr_parent) {
    let payload = $(`<div align="left">payload : ${data.payload}</div>`);
    let td = $('<td colspan="4"></td>').append(payload);
    let tr = $('<tr class="info"></tr>').append(td);
    // console.log($(that).get(0).tagName);
    $(tr_parent).after(tr);
}

function set_more(element){
  $(element).click(function(event) {
      console.log('more');
      type = $(this).parent().siblings('td:eq(1)').text();
      url = $(this).parent().siblings('td:eq(2)').text();
      that = $(this);
      tr_parent = $(that).parent().parent();
      console.log(type, url);
      if(!check_hide($(tr_parent))){
          $.ajax({
              url: `/momo/get_more_from_db?type=${type}&url=${escape(url)}`,
              dataType: 'json',
              // data: {searchWord: 'value1'}
          })
          .done(function(data) {
              console.log(data);
              if(type == 'SQL injection'){
                  addinfo_sql(data, tr_parent);
              }else if(type == 'XSS') {
                  addinfo_xss(data, tr_parent);
              }else if(type == 'Senstive file') {
                  addinfo_file(data, tr_parent);
              }else if(type == 'File inclusion') {
                  addinfo_lfi(data, tr_parent);
              }
              console.log("success");
              return data;
          })
          .fail(function() {
              console.log("error");
          })
          .always(function() {
              console.log("complete");
          });
      }
  });
}
