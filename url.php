<?php
print_r('run start here=========================================='.PHP_EOL);
/*
 * $node = [
 *    "name" => "",
 *    "child => "",
 *    "right" => "",
 *    "path" => [],
 * ];
 */

GLOBAL $nodes;
$nodes[1] = [
    'name' => '/',
    'path' => [],
    'child' => 2,
    'right' => 0
];
GLOBAL $id;
$id = 1;

const DEBUG = false;
function debug(){
    if(DEBUG){
        $args = func_get_args(); 
        print_r(PHP_EOL."DEBUG START.........".PHP_EOL);
        foreach($args as $k => $arg){
            print_r("arg {$k}:");
            print_r($arg);
            print_r(PHP_EOL);
        }
        print_r(PHP_EOL."DEBUG END.........".PHP_EOL);
    }
}

function insert($name='',$path='',$relationNode=0,$direction=''){
    GLOBAL $nodes;
    GLOBAL $id;
    debug($name,$path,$relationNode,$direction);
    $id++;
    $nodes[$id] = [
        'name' => $name,
        'path' => $path,
    ];
    if($relationNode && $direction){
        $nodes[$relationNode][$direction] = $id;
    }
    return $id;
}

function insertNode($domains=[],$path='',$currentNode=1,$direction='child'){
    GLOBAL $nodes;
    if(!$domains)return;
    $domain = array_shift($domains);
    $relationID = isset($nodes[$currentNode][$direction]) ? $nodes[$currentNode][$direction] :  0;
    if(isset($nodes[$relationID])){
        if($nodes[$relationID]['name'] == $domain){
            return insertNode($domains,$path,$relationID,'child');
        }else{
            while(isset($nodes[$relationID])  && $nodes[$relationID]['name'] != $domain){
                if(!isset($nodes[$relationID]['right']))break;
                $relationID = $nodes[$relationID]['right'];
            } 
            if($nodes[$relationID]['name'] != $domain){
                $relationID = insert($domain,$domains?[]:[$path],$relationID,'right');
            }
            return insertNode($domains,$path,$relationID,'child');
        }
    }else{
        $id = insert($domain,$domains?[]:[$path],$currentNode,$direction);
        return insertNode($domains,$path,$id,'child');
    }
}

function deleteNode($domains = [],$path = '',$currentNode=1,$direction='child'){
    GLOBAL $nodes;
}

function searchNode($domains = [],$path = '',$currentNode=1,$direction='child'){
    debug($domains,$path,$currentNode,$direction);
    GLOBAL $nodes;
    if(!$domains)return false;
    $domain = array_shift($domains); 
    $relationID = isset($nodes[$currentNode][$direction]) ? $nodes[$currentNode][$direction] :  0;
    if(isset($nodes[$relationID])){
        while($nodes[$relationID]['name'] != $domain){
            if(!isset($nodes[$relationID]['right']))return false;
            $relationID = $nodes[$relationID]['right'];
        }
    }
    if($path && !isset($nodes[$relationID]['path']) && !$nodes[$relationID]['path']){
        foreach($nodes[$relationID]['path'] as $_path){
            if(strpos($_path,$path) === 0)return true; 
        }
    }

    if(!isset($nodes[$relationID]['child'])){
        return true;
    }

    return searchNode($domains,$path,$relationID,'child');
}

function formartDomain($domains = [],$result = []){
    if(!$domains){
        return array_reverse($result);
    }else{
        $result[] = implode('.',$domains);
        array_shift($domains);
        return formartDomain($domains,$result);
    }
}

function formartURL($url){
    $url = parse_url($url);
    $domains = explode('.',$url['host']);
    $url['domains'] = formartDomain($domains);
    $url['path'] = isset($url['path']) ? $url['path'] : [];
    return $url;
}

function insertURL($url){
    $url = formartURL($url);
    return insertNode($url['domains'],$url['path']);
}

function deleteURL($url){
    $url = formartURL($url);
    return deleteNode($url['domains'],$url['path']);
}

function searchURL($url){
    print_r($url);
    $url = formartURL($url);
    return searchNode($url['domains'],$url['path']);
}

insertURL("http://www.baidu.com");
insertURL("http://test.api.viile.com");
insertURL("http://www.jd.com/video");
insertURL("http://www.taobao.com/pic");
insertURL("http://www.tudou.com/item");
insertURL("http://www.weibo.com/status");
insertURL("http://www.sina.com/timeline");
insertURL("http://www.zhihu.com/question");
insertURL("http://www.dlang.org/package");
insertURL("http://www.nginx.org/version");
insertURL("http://www.about.me/viile");
debug($nodes);

var_dump(searchURL("http://www.baidu.com"));
var_dump(searchURL("http://m.www.baidu.com"));
var_dump(searchURL("http://www.baidu.com/test"));
var_dump(searchURL("http://m.baidu.com"));
var_dump(searchURL("http://www.jd.com/video_test"));
var_dump(searchURL("http://api.viile.com"));
var_dump(searchURL("http://api.www.nginx.org"));
var_dump(searchURL("http://www.nginx.org/version_test"));
