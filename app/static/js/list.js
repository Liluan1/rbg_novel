$(document).ready(function () {     // dom树加载完成的时候，执行接下来的函数
    var content_url = $("#content_url").val();
    var chapter_url = $("#url").val();
    var novels_name = $("#novels_name").val();
    $(".container a").each(function () {    // each 遍历数组
        var url = $(this).attr('href');     // 当前的a标签中的herf值
        if (typeof(url) != "undefined") {   // if url未定义
            var name = $(this).text();      // a标签中的 text
            // 当content_url为1，表示该链接不用拼接
            if (content_url == '1') {
                content_url = ''
            } else if (content_url == '0') {
                // content_url=0表示章节网页需要当前url拼接
                content_url = chapter_url;
            } else if (content_url == '-1') {
                // content_url=-1 表示特殊情况
                content_url = chapter_url;
            }
            show_url = "/content?url=" + content_url + url + "&name=" + name + "&chapter_url=" + chapter_url + "&novels_name=" + novels_name;
            $(this).attr('href', show_url);     //将当前a标签中的herf设置为show_url
            $(this).attr('target', '_blank');   //
        }
    });
});