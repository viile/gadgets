<?php
class Test
{
    protected $_ioc;

    public function __construct($_ioc = null)
    {
        $this->_ioc = $_ioc;
    }

    public function __set($k,$v)
    {
        $this->$k = $v;
        return $this;
    }

    public function __get($k)
    {
        return $this->$k;
    }
 
    public function set($name,$function)
    {
        $this->$name = Closure::bind($function, $this, get_class());
    }
    
    public function __call($name,$args)
    {
        return call_user_func($this->$name, $args);
    }
}

class Session
{
    private $_config;

    public function __construct($config = [])
    {
        $this->_config = $config;
    }

    public function run()
    {
        print_r($this->_config);
        print_r(PHP_EOL);
    }
}

$conf = [
        'host' => 'localhost',
        'port' => 11211
];

$test = new Test();

$test->set('session',function() use($conf){
    return new Session($conf);
});

$test->cache = function() use($conf){
    return new Session($conf);
};

$tt = function() use ($conf){
    return new Session($conf);
};

$temp = new Session($conf);

$tt()->run();
$temp->run();
$test->cache()->run();
$test->session()->run();
