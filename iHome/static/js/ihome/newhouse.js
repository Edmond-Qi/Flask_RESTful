function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

// TODO: 在页面加载完毕之后获取区域信息
    $.get("/api/v1.0/areas", function (resp) {
        if (resp.errno == "0") {
            // 加载城区信息成功
            // 遍历设置所有城区的信息
            var areas = resp.data;

            /*
            for (var i=0; i<areas.length; i++) {
                // 获取每个城区信息
                var area = areas[i];
                // 向城区下拉列表框中添加option选择项
                $("#area-id").append('<option value="' + area.aid + '">' + area.aname + '</option>')
            }*/

            // 前端模板art_template
            var html = template("areas-tmpl", {"areas": areas});
            $("#area-id").append(html);
        }
        else {
            // 出错
            alert(resp.errmsg);
        }
    })

    // TODO: 处理房屋基本信息提交的表单数据
    $("#form-house-info").submit(function (e) {
        e.preventDefault();

        // 获取房屋的基本信息
        var house_params = {};
        $(this).serializeArray().map(function (x) {
            house_params[x.name] = x.value;
        })

        // 获取被选中的房屋设施的id
        var facility = [];
        $(":checked[name=facility]").each(function (index, item) {
            facility[index] = item.value;
        })

        house_params["facility"] = facility;

        // 请求发布房屋信息
        $.ajax({
            "url": "/api/v1.0/houses",
            "type": "post",
            "data": JSON.stringify(house_params),
            "contentType": "application/json",
            "headers": {
                "X-CSRFToken": getCookie("csrf_token")
            },
            "success": function (resp) {
                if (resp.errno == "0") {
                    // 发布房屋信息成功
                    // 隐藏房屋基本信息表单
                    $("#form-house-info").hide();
                    // 显示上传房屋图片的表单
                    $("#form-house-image").show();

                    // 设置上传房屋图片表单中房屋id
                    $("#house-id").val(resp.data.house_id);
                }
                else if (resp.errno == "4101") {
                    // 未登录
                    location.href = "login.html";
                }
                else {
                    // 出错
                    alert(resp.errmsg);
                }
            }
        })
    })

    // TODO: 处理图片表单的数据
    $("#form-house-image").submit(function (e) {
        e.preventDefault();

        // 请求上传房屋图片
        // 模拟表单提交行为
        $(this).ajaxSubmit({
            "url": "/api/v1.0/houses/image",
            "type": "post",
            "headers": {
                "X-CSRFToken": getCookie("csrf_token")
            },
            "success": function (resp) {
                if (resp.errno == "0") {
                    // 上传成功
                    // 设置在页面上显示上传的房屋图片
                    $(".house-image-cons").append('<img src="' + resp.data.img_url + '">');
                }
                else if (resp.errno == "4101") {
                    // 未登录
                    location.href = "login.html";
                }
                else {
                    // 出错
                    alert(resp.errmsg);
                }
            }
        })
    })

})