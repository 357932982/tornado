function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg(msg) {
    $(".popup>p").html(msg);
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

//日期加上天数得到新的日期
//dateTemp 需要参加计算的日期，days要添加的天数，返回新的日期，日期格式：YYYY-MM-DD
function getNewDay(dateTemp, days) {
    var dateTemp = dateTemp.split("-");
    var nDate = new Date(dateTemp[1] + '-' + dateTemp[2] + '-' + dateTemp[0]); //转换为MM-DD-YYYY格式
    var millSeconds = Math.abs(nDate) + (days * 24 * 60 * 60 * 1000);
    var rDate = new Date(millSeconds);
    var year = rDate.getFullYear();
    var month = rDate.getMonth() + 1;
    if (month < 10) month = "0" + month;
    var date = rDate.getDate();
    if (date < 10) date = "0" + date;
    return (year + "-" + month + "-" + date);
}

function showMoney(startDate, endDate){

    var sd = new Date(startDate);
    var ed = new Date(endDate);
    days = (ed - sd)/(1000*3600*24);
    var price = $(".house-text>p>span").html();
    var amount = days * parseFloat(price);
    $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
}

$(document).ready(function(){
    var startDate;
    var endDate;
    $.get("/api/check_login", function(data) {
        if ("0" != data.errcode) {
            location.href = "/login.html";
        }
    }, "json");
    $(".input-sm").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $("#start-date").change(function () {
        startDate = $("#start-date").val();
        endDate = getNewDay(startDate, 1)
        $("#end-date").val(endDate);
        showMoney(startDate, endDate);
    });
    $(".input-sm").on("changeDate", function(){
        startDate = $("#start-date").val();
        endDate = $("#end-date").val();
        if ("" == endDate || null == endDate){
           endDate = getNewDay(startDate, 1)
        }
        showMoney(startDate, endDate);

    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];
    $.get("/api/house/info?house_id=" + houseId, function(data){
        if ("0" == data.errcode) {
            $(".house-info>img").attr("src", data.data.images[0]);
            $(".house-text>h3").html(data.data.title);
            $(".house-text>p>span").html((data.data.price/100.0).toFixed(0));
        }
    }, "json");
    $(".submit-btn").on("click", function(e) {
        if ($(".order-amount>span").html()) {
            $(this).prop("disabled", true);
            var startDate = $("#start-date").val();
            var endDate = $("#end-date").val();
            var data = {
                "house_id":houseId,
                "start_date":startDate,
                "end_date":endDate
            };
            $.ajax({
                url:"/api/order",
                type:"POST",
                data: JSON.stringify(data), 
                contentType: "application/json",
                dataType: "json",
                headers:{
                    "X-XSRFTOKEN":getCookie("_xsrf"),
                },
                success: function (data) {
                    if ("4101" == data.errcode) {
                        location.href = "/login.html";
                    } else if ("4004" == data.errcode) {
                        showErrorMsg("房间已被抢定，请重新选择日期！"); 
                    } else if ("0" == data.errcode) {
                        location.href = "/orders.html";
                    }
                }
            });
        }
    });
})
