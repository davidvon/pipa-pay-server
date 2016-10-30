function formatTime(e) {
    var t = new Date(parseInt(1e3 * e)), i = new Date, s = Math.round(i.getTime() / 1e3) - e, a = i.getFullYear(), l = i.getMonth() + 1, n = i.getDate(), o = t.getFullYear(), r = t.getMonth() + 1, p = t.getDate(), d = t.getHours(), c = t.getMinutes();
    thatFullMinute = 10 > c ? "0" + c : c;
    var u; return u = 0 > s ? "刚刚" : a === o && l === r ? n === p ? 3600 > s ? 0 == parseInt(s / 60) ? "刚刚" : parseInt(s / 60) + "分钟前" : "今天 " + d + ":" + thatFullMinute : n === p + 1 ? "昨天 " + d + ":" + thatFullMinute : n === p + 2 ? "前天 " + d + ":" + thatFullMinute : r + "月" + p + "日 " + d + ":" + thatFullMinute : a === o && l !== r ? r + "月" + p + "日 " + d + ":" + thatFullMinute : o + "年 " + r + "月" + p + "日"
}

function render_booking_order(userid){
    var $message_count = $('.messages-menu a span');
    var $message_list =  $('.messages-menu .menu');
    var html = '';
    $.ajax({
        type: 'GET',
        url: '/api/customer/feedback?userid='+userid,
        contentType: 'application/json',
        success: function(data){
            var count = data.length;
            for( var i=0; i<count; i++)
                html += '<li><a href="/order/info/'+data[i].id+'">\
                    <div class="pull-left"><img src="'+data[i].head_img+'" class="img-circle"></div>\
                    <h4>'+data[i].nickname+'<small><i class="fa fa-clock-o" style="margin-right:2px;"></i>'+formatTime(data[i].timestamp)+'</small></h4>\
                    <p>'+data[i].num+'件</p></a></li>';
            $message_list.html(html);
            if(count>0){
                $message_count.html(count);
                $('.fa-shopping-cart').parent().find('small').html(count);
            }else{
                $message_count.html('');
                $('.fa-shopping-cart').parent().find('small').html('');
            }
        }
    });
}

function page_index_render(userid){
    var $message_count = $('.messages-menu a span');
    var $message_list =  $('.messages-menu .menu');
    $.ajax({
        type: 'GET',
        url: '/api/admin/home?userid='+userid,
        contentType: 'application/json',
        success: function(data){
            $('.user_today').text(data.customers_today);
            $('.user_total').text(data.customers_total);
            $('.visitors_today').text(data.visitors_today);
            $('.sales_today').text(data.sales_today);
            $('.orders_today').text(data.orders_today);
            var html = '';
            for( var i=0; i<data.customers_visit_top.length; i++)
                html += '<li> \
                      <img src="'+ data.customers_visit_top[i].customer.img +'" alt="User Image"/> \
                      <a class="users-list-name" href="#">'+ data.customers_visit_top[i].customer.name +'</a> \
                      <span class="users-list-date">'+ formatTime(data.customers_visit_top[i].customer.timestamp)+'</span> \
                    </li>';
            $('.visitor-users').html(html);
            html = '';
            for( var i=0; i<data.customers_register_top.length; i++)
                html += '<li> \
                      <img src="'+ data.customers_register_top[i].img +'" alt="User Image"/> \
                      <a class="users-list-name" href="#">'+ data.customers_register_top[i].name +'</a> \
                      <span class="users-list-date">'+ formatTime(data.customers_register_top[i].timestamp)+'</span> \
                    </li>';
            $('.register-users').html(html);
            html = '';
            for( var i=0; i<data.orders_top.length; i++) {
                var order_status_color = 'success';
                if (data.orders_top[i].status_code == 'booking') {
                    order_status_color = 'danger'
                } else if (data.orders_top[i].status_code == 'delivery') {
                    order_status_color = 'waring'
                } else if (data.orders_top[i].status_code == 'washing') {
                    order_status_color = 'primary'
                } else if (data.orders_top[i].status_code == 'received') {
                    order_status_color = 'info'
                }
                var pay_type_color = data.orders_top[i].paytype == '现金'?'info':'success';
                var paid_color = data.orders_top[i].paid == '未支付'?'waring':'success';
                html += '<tr><td><a href="/order/info/' + data.orders_top[i].id + '">' + data.orders_top[i].serial + '</a></td>\
                        <td>' + data.orders_top[i].customer.name + '</td><td>' + data.orders_top[i].customer.phone + '</td><td>' + data.orders_top[i].clothes + '</td>\
                        <td><span class="label label-'+order_status_color+'">' + data.orders_top[i].status + '</span></td><td><span class="label label-'+pay_type_color+'">' + data.orders_top[i].paytype + '</span></td>\
                        <td><span class="label label-'+paid_color+'">' + data.orders_top[i].paid + '</span></td>\
                        <td><div class="" data-color="#00a65a" data-height="20">' + data.orders_top[i].create_time + '</div></td></tr>'
            }
            $('.order_list').html(html);
        }
    });
}



