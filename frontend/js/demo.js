window.onload = function () {
    getNewData();
}


function showSearch(){
    var ttext = document.getElementById("seluser").value;
    showNow(ttext);
}
function showNow(keyy){

        places = 
        {"A":[118.787385,31.936507,"西门"],
        "B":[118.787065,31.942576,"北门"],
        "C":[118.798475,31.938689,"东门"],
        "D":[118.788744,31.941466,"樱花广场"],
        "E":[118.789559,31.940437,"体育中心"],
        "F":[118.795825,31.938234,"图书馆"],
        "G":[118.790846,31.937232,"1号楼主楼"],
        "H":[118.795851,31.934501,"南区宿舍"],
        "I":[118.794258,31.941156,"书香餐厅"],
        "X":[118.790846,31.937232,"计算机院楼"],
        "Y":[118.786887,31.940218,"游泳馆"],
        "Z":[118.788722,31.937469,"5号楼快递站"]}
    $.ajax({
        url: 'http://192.168.1.100:5000/api/history/' + keyy,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            //方法中传入的参数data为后台获取的数据
            var data1 = data['data'];
            var json = data1;
            // var json = JSON.parse(data1);
            pathh = json["path"].reverse();
            timee = json["time"].reverse();
            
            console.log(pathh,timee,"=+++");

            var dict_path1 = new Array();
            var dict_path1_zuobiao = new Array();
            var dict_time1 = new Array();

            for(var i=0;i<pathh.length;i++){
                dict_path1[i] = places[pathh[i]][2];
                dict_path1_zuobiao[i] = [places[pathh[i]][0],places[pathh[i]][1]];
                // dict_path1_zuobiao[i] = new Array([places[pathh[i]][0],places[pathh[i]][1]]);
                const words = timee[i].split('.');
                dict_time1[i] =  words[0]
            }

            // console.log(keyy,dict_path1,dict_time1,dict_path1_zuobiao);

            var show_path_now = document.getElementById("show_path_now");
            show_path_all.innerHTML = ""
            // keys = Object.keys(dict_path);

            var html1 = "<div style='text-align:center;'>"
            html1 += "<div>当前展示用户::"+keyy+"</div>";
            html1 += "<div>起点::"+dict_path1[0]+"";

            for(var i=1;i<dict_path1.length-1;i++){ 
                html1 += "->pass"+i+"::"+dict_path1[i]+"("+dict_time1[i]+")";
            }

            html1 += "->"+dict_path1[dict_path1.length-1]+"::终点</div>";
            html1 += "</div>"
            show_path_now.innerHTML = html1;
            console.log(keyy,dict_path1_zuobiao[0],"00066");
            markpath(keyy,dict_path1_zuobiao)
        }
    })
}

function markpath(username,path){
        
        // path_now = dict_path[username];
        // console.log(path_now);
        start_point = new AMap.LngLat(path[0][0],path[0][1]);
        end_point = new AMap.LngLat(path[path.length-1][0],path[path.length-1][1]);
        var ll_path = new Array(path.length-2);
        for(var i=1;i<path.length-1;i++){
            ll_path[i-1] = new AMap.LngLat(path[i][0],path[i][1]);
        }
    

    // 根据起终点经纬度规划驾车导航路线
    // driving.search(new AMap.LngLat(118.787953,31.939608), new AMap.LngLat(118.795839,31.935401),{
    //     waypoints:[new AMap.LngLat(118.793553,31.940828),new AMap.LngLat(118.790373,31.938046)]
    driving.search(start_point, end_point,{
        waypoints:ll_path
    }, function(status, result) {
        // result 即是对应的驾车导航信息，相关数据结构文档请参考  https://lbs.amap.com/api/javascript-api/reference/route-search#m_DrivingResult
        if (status === 'complete') {
            log.success('绘制驾车路线完成')
        } else {
            log.error('获取驾车数据失败：' + result)
        }
    });
    };

function getNewData() {

    places = 
        {"A":[118.787385,31.936507,"西门"],
        "B":[118.787065,31.942576,"北门"],
        "C":[118.798475,31.938689,"东门"],
        "D":[118.788744,31.941466,"樱花广场"],
        "E":[118.789559,31.940437,"体育中心"],
        "F":[118.795825,31.938234,"图书馆"],
        "G":[118.790846,31.937232,"1号楼主楼"],
        "H":[118.795851,31.934501,"南区宿舍"],
        "I":[118.794258,31.941156,"书香餐厅"],
        "X":[118.790846,31.937232,"计算机院楼"],
        "Y":[118.786887,31.940218,"游泳馆"],
        "Z":[118.788722,31.937469,"5号楼快递站"]}
    

    ttt = '[{"user":1,\
        "path":["X","G","Z"],\
        "time":["1606559675", "1606579975", "1606580244"],\
        "faceID":1},\
        {"user":2,\
        "path":["F","D","E"],\
        "time":["1606559675", "1606579975", "1606580244"],\
        "faceID":2},\
        {"user":3,\
        "path":["G","Y","H"],\
        "time":["1606559675", "1606579975", "1606580244"],\
        "faceID":3},\
        {"user":4,\
        "path":["G","D","B"],\
        "time":["1606559675", "1606579975", "1606580244"],\
        "faceID":4},\
        {"user":5,\
        "path":["X","G","A"],\
        "time":["1606559675", "1606579975", "1606580244"],\
        "faceID":5}]'



    function showAll(dict_path,dict_time){
        var show_path_all = document.getElementById("show_path_all");
        show_path_all.innerHTML = ""
        keys = Object.keys(dict_path);
        for(var i=0;i<keys.length;i++){
            var opt = document.createElement("div");
            opt.innerHTML = "<div style='text-align:center;top:20px;position: relative;' onclick='showNow("+keys[i]+")'><div  style='text-align:center;'>当前用户::"+keys[i] + dict_path[keys[i]] + dict_time[keys[i]]+"</div></div><br>";
            show_path_all.appendChild(opt);
        }
    }


    // showAll();
//------------------------------------------------
    

    //设置时间 5-秒  1000-毫秒  这里设置你自己想要的时间 
    setTimeout(getNewData,2*1000);
    $.ajax({
        url: 'http://192.168.1.100:5000/api/realtime',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            //方法中传入的参数data为后台获取的数据
            var data1 = data['data'];
            var json = data1;
            // var json = JSON.parse(data1);
            // console.log(json);

            var dict_path = {}
            var dict_time = {}

            for(var i=json.length-1;i>=0;i--){
                dict_path[json[i].person] = places[json[i].location][2];

                timee = json[i].time
                const words = timee.split('.');
                dict_time[json[i].person] =  words[0]
            }

            showAll(dict_path,dict_time);


        }
    })
}