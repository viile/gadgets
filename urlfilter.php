<?php

GLOBAL $nodes;
GLOBAL $node_path;
$node_path = [];
$nodes[1] = [
    'name' => '/',
    'tags' => '',
    'attribute' => 0,
    'child' => 0,
    'brother' => 0
];
GLOBAL $id;
GLOBAL $node_path_i;

class urlfilter
{
    private $urlModel;
    private $urlPathModel;
    private $host;
    private $path;
    private $tags;
    private $attributes = [
        'none' => 0,
        'onlyDomain' => 1,
        'onlyPath' => 2,
        'all' => 3,
    ];

    function __construct()
    {
        $this->urlModel = new urlModel();
        $this->urlPathModel = new urlPathModel();   
    }

    public function insertURL($url = '' ,$tags = '')
    {
        if(!$url || !$tags)
        {
            return;
        }

        $url = $this->formatURL($url);
        print_r($url);
        $this->tags = $tags;
        $this->path = $url['path'];
        $this->host = $url['host'];
        return $this->insertNode($url['domains']);
    }

    public function deleteURL($url = '',$tags = '')
    {
        if(!$url || !$tags)
        {
            return;
        }

        $url = $this->formatURL($url);
        $this->tags = $tags;
        $this->path = $url['path'];
        $this->host = $url['host'];
        return $this->deleteNode($url['domains']); 
    }

    private function insertNode($domains = [],$currentNode = 1)
    {
        if(!$domains)return;
        $domain = array_pop($domains);
        $isLastNode = $domains ? false : true;
        $current = $this->urlModel->getDataByID($currentNode);
        if(isset($current['child']) && $current['child'])
        {
            $relationNode = $this->urlModel->getDataByID($current['child']);
            while(isset($relationNode['name']) && $relationNode['name'] != $domain &&
                isset($relationNode['brother']) && $relationNode['brother'])
            {
                $relationNode = $this->urlModel->getDataByID($relationNode['brother']);
            }
            if($relationNode['name'] != $domain)
            {
                $id = $this->insert($domain,$relationNode['id'],'brother');
                return $this->insertNode($domains,$id);
            }
            else
            {
                if($isLastNode)
                {
                    $attribute = $this->attributes['none']; 
                    if($this->path)
                    {
                        $this->urlPathModel->insert($relationNode['id'],$this->path,$this->tags);
                        $attribute = $relationNode['attribute'] | $this->attributes['onlyPath'];
                    }
                    else
                    {
                        $attribute = $relationNode['attribute'] | $this->attributes['onlyDomain'];
                    }
                    $tags = $relationNode['tags'];
                    if($relationNode['tags'])
                    {
                        $tags = implode(',',array_unique(explode(',',$tags.','.$this->tags)));
                    }
                    return $this->urlModel->update($relationNode['id'],[
                        'attribute'=>$attribute,
                        'tags'=>$tags
                    ]);
                }
                return $this->insertNode($domains,$relationNode['id']);
            }    
        }
        else
        {
            $id = $this->insert($domain,$currentNode); 
            if($isLastNode)
            {
                return $id;
            }
            return $this->insertNode($domains,$id);
        }
    }

    private function insert($domain = '',$relationNode = 0,$direction = 'child')
    {
        $attribute = $this->attributes['none'];
        $tags = '';
        if($domain == $this->host)
        {
            $attribute = $this->path ? $this->attributes['onlyPath'] : $this->attributes['onlyDomain'];
            $tags = $this->tags;
        }
        $id = $this->urlModel->insert($domain,$tags,$attribute);
        if($domain == $this->host && $this->path)
        {
            $this->urlPathModel->insert($id,$this->path,$this->tags);
        }
        if($relationNode)
        {
            $this->urlModel->update($relationNode,[$direction => $id]);
        }
        return $id;
    }

    private function formatURL($url = ''){
        print_r($url);
        $url = parse_url($url);
        $domains = explode('.',$url['host']);
        $url['domains'] = $this->formartDomain($domains);
        $url['path'] = isset($url['path']) ? $url['path'] : [];
        return $url;
    }

    private function formartDomain($domains = [],$result = []){
        if(!$domains)
        {
            return $result;
        }
        else
        {
            $result[] = implode('.',$domains);
            array_shift($domains);
            return $this->formartDomain($domains,$result);
        }
    }
}

class Model
{
    public function insert(){}
    public function query(){}
    public function update(){}
    public function remove(){}
}

class urlModel extends Model
{
    public function getDataByID($id)
    {
        GLOBAL $nodes;
        $node = isset($nodes[$id]) ? $nodes[$id] : [];
        if($node)
        {
            $node['id'] = $id;
        }
        return $node;
    } 
    
    public function insert($domain = '',$tags = '',$attribute=0)
    {
        GLOBAL $nodes;
        $i = count($nodes) + 1;
        $nodes[$i] = [
            'name' => $domain,
            'tags' => $tags,
            'attribute' => $attribute,
        ];
        return $i;
    } 

    public function update($id = 0,$columnsToModify = [])
    {
        GLOBAL $nodes;
        foreach($columnsToModify as $key => $value)
        {
            $nodes[$id][$key] = $value;
        }
    }
}

class urlPathModel extends Model
{
    public function insert($url_id = 0,$path = '',$tags='')
    {
        GLOBAL $node_path;
        $i = count($node_path) + 1;
        $node_path[$i] = [
            'url_id' => $url_id,
            'path' => $path,
            'tags' => $tags,
        ];

        return $i;
    }
}


$filter = new urlfilter();
$filter->insertURL("http://www.taobao.com","1");
$filter->insertURL("http://www.taobao.com","2");
$filter->insertURL("http://www.taobao.com/product/","1");
$filter->insertURL("http://www.taobao.com/video/","3");
$filter->insertURL("http://taobao.com","3");
$filter->insertURL("http://www.baidu.com","2");
$filter->insertURL("http://www.youku.com/test/","6");
$filter->insertURL("http://api.baidu.com","3");
$filter->insertURL("http://www.jd.com/item/","4");
$filter->insertURL("http://www.jd.com/test/","4");

print_r($nodes);
print_r($node_path);

/*
DROP TABLE IF EXISTS `url`;
CREATE TABLE `url` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(255) DEFAULT NULL,
    `tags` varchar(255) DEFAULT NULL,
    `child` int(11) unsigned DEFAULT '0',
    `brother` int(11) unsigned DEFAULT '0',
    `attribute` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0 不生效 1仅匹配域名  2 仅匹配path 3 匹配域名和path',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `url`;
CREATE TABLE `url_path` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `url_id` int(11) DEFAULT NULL,
    `path` varchar(255) DEFAULT NULL,
    `tags` int(11) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
 */


