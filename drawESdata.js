var Discover = {
    graph : function() {
        var event_id = $('#event_id').val().trim();
        var url = "http://"+ES_HOST+"/logs/event/_search?pretty=true&q=event_id:";
        if(event_id){
            $.get(url+ event_id,{},function(result,status,xhr){
                if (status == "success") {
                    if(result.hits.total == 0) {
                        swal("wrong!", "data not found", "error");	
                    } else {
                        var tree = Draw.formatESdata(result.hits.hits);
                        var option = Draw.convertToEChartsData(tree);
                        var myChart = echarts.init(document.getElementById('TreeGraph'));
                        myChart.setOption(option);
                    }
                } else {
                    swal("wrong!", "network error", "error");	
                }
            },'json');
        }else{
            swal("wrong!", "not input data", "error");
        }
    },
};

var Draw = {
    depths:[],
    spans:{},
    event_id:"",
    canvasHeigth:1200,
    canvasWeigth:2000,
    position : {},
    formatESdata : function(data){
        var result = {};
        var tree = Draw.buildTree(data,0,1,1);
        Draw.depth(tree,1);
        Draw.spans[0] = 1;
        result["tree"] = tree;
        result["maxDepth"] = Draw.maxDepth() + 1;
        result["maxSpan"] = Draw.maxSpan();
        result["event_id"] = Draw.event_id;
        result["depths"] = Draw.depths;
        result["spans"] = Draw.spans;
        result["canvasHeigth"] = Draw.canvasHeigth;
        result["canvasWeigth"] = Draw.canvasWeigth;
        return result;
    },
    multiPR : function(n){
        var r = "";
        while(n>0){
            r += "<p>";
            n--;
        }
        return r;
    },
    formatJsonData : function(str){
        var len = str.length;
        var level = 0;
        var index = 0;
        var result;
        var flag = ["{","[","}","]",","];
        var upLvl = ["{","["];
        var downLvl = ["}","]"];
        while(index < len){
            if($.inArray(str[index],upLvl))level++;
            if($.inArray(str[index],downLvl))level--;
            if($.inArray(str[index],flag)){
                result = result + (str[index] + "<br>" + Draw.multiPR(level)); 
            }else{
                result += str[index];
            }
            index++;
        }
        return result;
    },
    convertToEChartsData : function(data){
        var option = {
            animationDurationUpdate: 1500,
            animationEasingUpdate: 'quinticInOut',
            animationDelay: function (idx) {
                return idx * 300;
            },
            tooltip : {
                trigger : "item",
                enterable : true,
                confine : true,
                position: ['1%', '1%'],
                backgroundColor : '#fff',
                textStyle : {
                    color : '#000',
                },
                //alwaysShowContent : true,
                extraCssText : 'pre {outline: 1px solid #ccc; padding: 5px; margin: 5px; };.string { color: green; };.number { color: darkorange; };.boolean { color: blue; };.null { color: magenta; };.key { color: red; };', 
                formatter: function(params){
                    var str = '';
                    if (params.dataType == "node") {
                        str = Draw.syntaxHighlight(JSON.stringify(params.data.value["value"]["_source"], null, 2));
                    } else if (params.dataType == "edge") {
                        str = Draw.syntaxHighlight(JSON.stringify(params.data, null, 2));
                    }
                    return '<pre id="result">' + str + "</pre>";
                }
            },
            series : [
                {
                    type: 'graph',
                    layout: 'none',
                    symbolSize: 50,
                    roam: true,
                    label: {
                        normal: {
                            show: true
                        }
                    },
                    edgeSymbol: ['circle', 'arrow'],
                    edgeSymbolSize: [4, 10],
                    edgeLabel: {
                        normal: {
                            show : false,
                            textStyle: {
                                fontSize: 10
                            }
                        }
                    },
                    data: [],
                    links: [],
                    lineStyle: {
                        normal: {
                            opacity: 0.9,
                            width: 2,
                            curveness: 0
                        }
                    }
                }]
        };
        option["title"] = {"text":"事件"+data["event_id"]+"流程"};

        Draw.addEChartsData(option,data["tree"],0);

        return option;
    },
    addEChartsData : function(option,node,lvl){
        if(!(node["depth"] in Draw.position))Draw.position[node["depth"]] = 0;
        Draw.position[node["depth"]] = Draw.position[node["depth"]] + 1;
        var name = node["depth"] + "," + node["span"] + "," + node["value"]["_id"];
        option["series"][0]["data"].push({
            "name" : name,
            "x" : (Draw.canvasWeigth / (Draw.maxDepth() + 1)) * node["depth"],
            "y" : (Draw.canvasHeigth / (Draw.spans[lvl] + 1)) * Draw.position[node["depth"]],
            "symbolSize":100,
            value : node,
            label : {
                normal : {
                    show : true,
                    position : "bottom",
                    color : "#fff",
                    fontWeight : "bold",
                    fontSize : 15,
                }
            },
            itemStyle: {
                normal: {
                    color: (("flag" in node.value) ? 'red' :  'green')
                }
            }
        });
        if(node["childs"].length){
            $.each(node["childs"],function(index,obj){
                var link = {
                    "source" : name,
                    "target" : obj["depth"] + "," + obj["span"] + "," + obj["value"]["_id"]
                };
                option["series"][0]["links"].push(link);
                Draw.addEChartsData(option,obj,lvl+1);
            });
        }
    },
    buildTree : function(data,msg_id,span,depth){
        var node = {};
        var canFind = false;
        $.each(data,function(index,obj){
            if(obj._source.msg_id == msg_id){
                canFind = true;
                if(!Draw.event_id)Draw.event_id = obj._source.event_id;
                var id = obj._id;
                node["value"] = obj;
                node["span"] = span;
                node["depth"] = depth;
                node["childs"] = [];
                if('sub_requests' in obj._source && obj._source.sub_requests != null){
                    $.each(obj._source.sub_requests,function(index,obj){
                        node["childs"].push(Draw.buildTree(data,obj.msg_id,index + 1,depth + 1));
                    });
                }
            }
        });
        if(!canFind){
            node["value"] = {
                "_id" : msg_id,
                "flag" : "virtual",
                "_source" : {}
            };
            node["span"] = span;
            node["depth"] = depth;
            node["childs"] = [];
        }
        return node;
    },
    maxDepth : function(){
        var max = 0;
        $.each(Draw.depths,function(v){max = v > max ? v : max;});
        return max;
    },
    maxSpan : function(){
        var max = 0;
        $.each(Draw.spans,function(index,v){max = v > max ? v : max;});
        return max;
    },
    depth: function(tree,currDepth){
        if(tree["childs"].length){
            if(!(currDepth in Draw.spans))Draw.spans[currDepth] = 0;
            Draw.spans[currDepth] += tree["childs"].length;
            var nextDepth = currDepth + 1;
            $.each(tree["childs"],function(index,obj){
                Draw.depth(obj,nextDepth);
            });
        }else{
            Draw.depths.push(currDepth);
        }
    },
    syntaxHighlight : function(json) {
        if (typeof json != 'string') {
            json = JSON.stringify(json, undefined, 2);
        }
        json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
            var cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            var str = '<span class="' + cls + '">' + match + '</span>';
            return str;
        });
    },
    test : function(str){
        console.log("NOTICE:" + str);
    },
};
