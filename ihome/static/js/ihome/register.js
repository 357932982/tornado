function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    var picId = generateUUID();
    imageCodeId = $("input[name='imagecode']").attr('id');
    $(".image-code img").attr("src", "/api/piccode?codeid="+picId+"&pre_code_id="+imageCodeId);
    $("input[name='imagecode']").attr('id', picId);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!/^1\d{10}$/.test(mobile)) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var piccode = $("input[name='imagecode']").val();
    var imageCode = $("input[name='imagecode']").attr("id");
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // $.get("/api/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId},
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg);
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒");
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码');
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60);
    //         }
    // }, 'json');
    var data = {mobile:mobile, piccode:piccode, piccode_id:imageCode};
    $.ajax({
        url: "/api/smscode",
        method: "post",
        headers: {
            "X-XSRFTOKEN": getCookie("_xsrf"),
        },
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",
        success: function (data) {
            // data = {
            //     errcode
            //     errmsg
            // }
            if ("0" == data.errcode) {
                var duration = 60;
                var timeObj = setInterval(function () {
                    duration = duration - 1;
                    $(".phonecode-a").html(duration+"秒");
                    if (1 == duration) {
                        clearInterval(timeObj);
                        $(".phonecode-a").html("获取验证码");
                        $(".phonecode-a").attr("onclick", "sendSMSCode();")
                    }
                }, 1000, 60)
            } else {
                $("#image-code-err1 span").html(data.errmsg);
                $("#image-code-err1").show();
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                if (data.errcode == "4002" || data.errcode == "4004") {
                    generateImageCode();
                }
            }
        }
    })

}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
        $("#image-code-err1").hide();
    });
    $("input[name='imagecode']").focus(function(){
        $("#image-code-err").hide();
        $("#image-code-err1").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // 当用户点击表单提交按钮时执行自己定义的函数
    $(".form-register").submit(function(e){
        // 阻止浏览器对于表单的默认行为
        e.preventDefault();
        var mobile = $("#mobile").val();
        var phonecode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        // 校验用户填写的参数
        if (!/^1\d{10}$/.test(mobile)) {

            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phonecode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        // 声明一个要保存结果的变量
        var data = {};
        // 把表单中的数据填充到data中
        $(".form-register").serializeArray().map(function(x){data[x.name]=x.value});
        // 把data变量转为josn格式字符串
        var json_data = JSON.stringify(data);
        //向后端发送请求
        $.ajax({
            url: "/api/register",
            method: "POST",
            data: json_data,
            contentType: "application/json", // 告诉后端服务器，发送的请求数据是json格式的
            dataType: "json",   // 告诉前端，收到的响应数据是json格式的
            headers: {
                "X-XSRFTOKEN": getCookie("_xsrf"),
            },
            success: function (data) {
                if ("0" == data.errcode) {
                    location.href = "/";
                } else if ("验证码过期" == data.errmsg || "验证码错误" == data.errmsg) {
                    $("#phone-code-err>span").html(data.errmsg);
                    $("#phone-code-err").show();
                }

            }
        })
    });


// $(".form-register").serializeArray()
//     li = [Object, Object, Object, Object, Object]
//     [0:Object
//         name: "mobile"
//         value: "18111111111"
//
//     1:Object
//         name: "phonecode"
//         value: "1234"
//             ...
//     ]
//
//     {
//         mobile: 181111111,
//             phonecode: 1234
//     }
//
//     $(".form-register").serializeArray().map(action)
//
// for ele in li:
//     fun(ele)
//
//
//     dict = {}
//
//     function action(x){
//         x.name
//         x.value
//         dict[x.name] = x.value
//     }





























})