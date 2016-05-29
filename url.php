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

function debug(){
    $args = func_get_args(); 
    print_r(PHP_EOL."DEBUG START.........".PHP_EOL);
    foreach($args as $k => $arg){
        print_r("arg {$k}:");
        print_r($arg);
        print_r(PHP_EOL);
    }
    print_r(PHP_EOL."DEBUG END.........".PHP_EOL);
}
/*
function insertNode($domains = [],$path='',$relationNode = "",$direction = ""){
    GLOBAL $nodes;
    debug($domains,$path,$relationNode,$direction);
    if(!$domains)return;
    $domain = array_shift($domains);
    //如果当前节点不存在
    if(!isset($nodes[$domain])){
        $id = count($nodes) + 1;
        $nodes[$id] = [
            'name' => $domain,
        ];
        //如果当前节点是域名最后一个节点,而且存在$path
        if(!$domains && $path){
            $nodes[$id]['path'] = $path;
        }
        //如果该节点不是顶级域名,修改关系节点
        if($relationNode && $direction){
            $nodes[$relationNode][$direction] = $id;
        }
        return insertNode($domains,$path,$id,'child');
    }
    //逼近关系节点
    if(isset($relationNode[$direction])){
    
    }
    return insertNode($domains,$path);
}
 */

function insert($name='',$path='',$relationNode=0,$direction=''){
    GLOBAL $nodes;
    GLOBAL $id;
    //debug($name,$path,$relationNode,$direction);
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

function deleteNode($relationNode = 0,$domains = [],$path = ""){
    GLOBAL $nodes;
}

function searchNode($relationNode = 0,$domains = [],$path = ""){
    GLOBAL $nodes;
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
    return $url;
}

function insertURL($url){
    $url = formartURL($url);
   // print_r($url);
    return insertNode($url['domains'],$url['path']);
}

function deleteURL($url){
    $url = formartURL($url);
    return deleteNode($url['domains'],$url['path']);
}

//print_r(formartURL("http://www.baidu.com/video/"));
//print_r($nodes);
insertURL("http://www.baidu.com/video/");
insertURL("http://www.jd.com/videoi");
/*
insertURL("http://www.taobao.com/videoi");
insertURL("http://www.tudou.com/videoi");
insertURL("http://www.weibo.com/videoi");
insertURL("http://www.sina.com/videoi");
insertURL("http://www.zhihu.com/videoi");
 */
insertURL("http://www.dlang.org/videoi");
insertURL("http://www.nginx.org/videoi");
insertURL("http://www.about.me/videoi");
print_r($nodes);
