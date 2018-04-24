function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// TODO: 点击推出按钮时执行的函数
function logout() {
    // 请求退出登录
    $.ajax({
        "url": "/api/v1.0/session",
        "type": "delete",
        "headers": {
            "X-CSRFToken": getCookie("csrf_token")
        },
        "success": function (resp) {
            if (resp.errno == '0') {
                // 退出登录之后跳转到首页
                location.href = '/';
            }
        }
    })
    
}

$(document).ready(function(){

    // TODO: 在页面加载完毕之后去加载个人信息
    $.get('/api/v1.0/user', function (resp) {
        if (resp.errno == '0') {
            // 获取信息成功
            // 设置用户的头像地址，用户名和手机号
            $('#user-avatar').attr('src', resp.data.avatar_url);
            $('#user-name').html(resp.data.username);
            $('#user-mobile').html(resp.data.mobile);
        }
        else if (resp.errno == '4101') {
            // 用户未登录，跳转到登录页面
            location.href = 'login.html';
        }
        else {
            // 获取信息失败
            alert(resp.errmsg);
        }
    })

});
