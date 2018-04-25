function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // TODO: 查询用户的实名认证信息
    $.get("/api/v1.0/user/auth", function (resp) {
        if(resp.errno == "0"){
            // 获取实名认证成功
            if(resp.data.real_name && resp.data.id_card){
                // 设置用户实名认证的认证信息
                $("#real-name").val(resp.data.real_name);
                $("#id-card").val(resp.data.id_card);
                // 禁用姓名输入框和身份证号输入框
                $("#real-name").attr("disabled", true);
                $("#id-card").atttr("disabled", true);
                // 隐藏实名认证的提交按钮
                $(".btn-success").hide();
            }
        }
        else if (resp.errno == "4101"){
            // 用户未登录，跳转等到登陆页
            location.href = "login.html"
        }
        else{
            // 出错，弹出出错信息
            alert(resp.errmsg);
        }

    })


    // TODO: 管理实名信息表单的提交行为
    $("#form-auth").submit(function (e) {
        // 组织表单默认提交行为
        e.preventDefault();

        // 请求进行实名的认证
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();

        if (!real_name || !id_card) {
            $(".error-msg").show();
            return;
        }
        $(".error-msg").hide();

        var params = {
            "real_name": real_name,
            "id_card": id_card
        }

        $.ajax({
            "url": "/api/v1.0/user/auth",
            "type": "post",
            "data": JSON.stringify(params),
            "contentType": "application/json",
            "headers": {
                "X-CSRFToken": getCookie("csrf_token")
            },
            "success": function (resp) {
                if (resp.errno == "0") {
                    // 实名认证成功
                    // 禁用姓名输入框和身份证号输入框
                    $("#real-name").attr("disabled", true);
                    $("#id-card").attr("disabled", true);
                    // 隐藏实名认证提交按钮
                    $(".btn-success").hide();
                }
                else if (resp.errno == "4101") {
                    // 用户未登录，跳转到登录页面
                    location.href = "login.html";
                }
                else {
                    // 实名认证失败
                    alert(resp.errmsg);
                }
            }
        })
    })

})