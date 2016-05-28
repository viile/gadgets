<?php

/*
 * $node = [
 *    "name" => "",
 *    "child => "",
 *    "right" => "",
 *    "path" => [],
 * ];
 */

GLOBAL $nodes;

function debug(){
    $args = func_get_args(); 
    print_r(PHP_EOL."DEBUG.........".PHP_EOL);
    foreach($args as $k => $arg){
        print_r("arg {$k}:");
        print_r($arg);
        print_r(PHP_EOL);
    }
    print_r(PHP_EOL."DEBUG.........".PHP_EOL);
}
function insertNode($domains = [],$path='',$relationNode = "",$direction = ""){
    GLOBAL $nodes;
    debug($domains,$path,$relationNode,$direction);
    if(!$domains)return;
    $domain = array_shift($domains);
    //如果当前节点不存在
    if(!isset($nodes[$domain])){
        $nodes[$domain] = [
            'name' => $domain,
        ];
        //如果当前节点是域名最后一个节点,而且存在$path
        if(!$domains && $path){
            $nodes[$domain]['path'] = $path;
        }
        //如果该节点不是顶级域名,修改关系节点
        if($relationNode && $direction){
            $nodes[$relationNode][$direction] = $domain;
        }
        return insertNode($domains,$path,$domain,'child');
    }
    //逼近关系节点
    if(isset($relationNode[$direction])){
    
    }
    return insertNode($domains,$path);
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
    return insertNode($url['domains'],$url['path']);
}

function deleteURL($url){
    $url = formartURL($url);
    return deleteNode($url['domains'],$url['path']);
}

//print_r(formartURL("http://www.baidu.com/video/"));
insertURL("http://www.baidu.com/video/");
print_r($nodes);
