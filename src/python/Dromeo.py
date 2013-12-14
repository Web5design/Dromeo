<?php
/**
*
*   Dromeo
*   Simple HTTP Routing Framework for PHP, Python, Node
*
*   https://github.com/foo123/Dromeo
*
*   Inspired and Based on: https://github.com/Dachande663/PHP-Router, by Luke Lanchester
*
**/
class Dromeo 
{
    
    const VERSION = "0.1";
    
    private static $httpMethods = array('GET', 'POST', 'PUT', 'DELETE');

    private static $httpStatusCodes = array(
        '100' => 'Continue',
        '101' => 'Switching Protocols',
        '102' => 'Processing',

        '200' => 'OK',
        '201' => 'Created',
        '202' => 'Accepted',
        '203' => 'Non-Authoritative Information',
        '204' => 'No Content',
        '205' => 'Reset Content',
        '206' => 'Partial Content',
        '207' => 'Multi-Status',
        '226' => 'IM Used',

        '300' => 'Multiple Choices',
        '301' => 'Moved Permanently',
        '302' => 'Found',
        '303' => 'See Other',
        '304' => 'Not Modified',
        '305' => 'Use Proxy',
        '306' => 'Reserved',
        '307' => 'Temporary Redirect',

        '400' => 'Bad Request',
        '401' => 'Unauthorized',
        '402' => 'Payment Required',
        '403' => 'Forbidden',
        '404' => 'Not Found',
        '405' => 'Method Not Allowed',
        '406' => 'Not Acceptable',
        '407' => 'Proxy Authentication Required',
        '408' => 'Request Timeout',
        '409' => 'Conflict',
        '410' => 'Gone',
        '411' => 'Length Required',
        '412' => 'Precondition Failed',
        '413' => 'Request Entity Too Large',
        '414' => 'Request-URI Too Long',
        '415' => 'Unsupported Media Type',
        '416' => 'Requested Range Not Satisfiable',
        '417' => 'Expectation Failed',
        '422' => 'Unprocessable Entity',
        '423' => 'Locked',
        '424' => 'Failed Dependency',
        '426' => 'Upgrade Required',

        '500' => 'Internal Server Error',
        '501' => 'Not Implemented',
        '502' => 'Bad Gateway',
        '503' => 'Service Unavailable',
        '504' => 'Gateway Timeout',
        '505' => 'HTTP Version Not Supported',
        '506' => 'Variant Also Negotiates',
        '507' => 'Insufficient Storage',
        '510' => 'Not Extended'
    );

    private $options = array(
        'supportPost' => true
    );


    private $routes = array(
        'GET'    => array(),
        'POST'   => array(),
        'PUT'    => array(),
        'DELETE' => array(),
    );

    private $fallback = array();
    
    private $baseUrl = '';
    
    
    public function __construct($base='', array $options=null) 
    {
        $this->baseUrl = $base;
        if (null !== $options) $this->options = array_merge($this->options, $options);
    }


    public function Dromeo($base='', $options=null)
    {
        return $this->__construct($base, $options)
    }
    
    public function On(array $methods, $pattern, $options, $callback = null) 
    {
        if( !$callback && is_callable($options) ) 
        {
            $callback = $options;
            $options = null;
        }
        
        // use an optional baseurl
        $pattern = $this->baseUrl . $pattern;
        
        $route = array(
            'pattern'  => $pattern,
            'callback' => $callback
        );

        $route = ($options && is_array($options)) ? array_merge($route, $options) : $route;
        
        $methods = (array)$methods;
        
        foreach($methods as $method) 
        {
            $method = strtoupper($method);
            if ( in_array($method, self::$methods) )
            {
                $this->routes[ $method ][] = $route;
            }
        }

        return $this;
    }
    
    public function Get($pattern, $options, $callback = null) 
    {
        return $this->On('GET', $pattern, $options, $callback);
    }



    public function Post($pattern, $options, $callback = null) 
    {
        return $this->On('POST', $pattern, $options, $callback);
    }



    public function Put($pattern, $options, $callback = null) 
    {
        return $this->On('PUT', $pattern, $options, $callback);
    }



    public function Delete($pattern, $options, $callback = null) 
    {
        return $this->On('DELETE', $pattern, $options, $callback);
    }



    public function Any($pattern, $options, $callback = null) 
    {
        return $this->On(array('GET', 'POST'), $pattern, $options, $callback);
    }



    public function All($pattern, $options, $callback = null) 
    {
        return $this->On(self::$httpMethods, $pattern, $options, $callback);
    }



    public function notFound($callback, $options=array()) 
    {
        $this->fallback = array('callback'=>$callback, 'options'=>$options);
        return $this;
    }
    

    public function setBaseUrl($base='')
    {
        $this->baseUrl = $base;
        return $this;
    }
    
    public function route(/* var args here .. */) 
    { 
        $args = func_get_args();
        if ( isset($args[0]) && is_array($args[0]) )  $args = $args[0];
            
        return preg_replace('/\/+/', '/', $this->baseUrl .  '/' . implode('/', $args) ); 
    }

    
    // adapted from WordPress
    public function setStatusHeader( $code ) 
    {
        $code = strval( intval( $code ) );
        
        if ( !isset( self::$httpStatusCodes[ $code ] ) )  return false;
        
        $text = self::$httpStatusCodes[ $code ];
        
        $protocol = $_SERVER["SERVER_PROTOCOL"];
        if ( 'HTTP/1.1' != $protocol && 'HTTP/1.0' != $protocol )  $protocol = 'HTTP/1.0';
        $status_header = "$protocol $code $text";

        return @header( $status_header, true, intval($code) );
    }
    
    public function parseUri($uri)
    {
        $parts = parse_url($uri);
        
        if ( isset($parts['query']) )
            parse_str($parts['query'], $queryParams);
        
        else
            $queryParams = array();
        
        $parts = array_merge( $parts, array('queryParams'=>$queryParams) );
        
        return $parts;
    }
    
    public function buildUri($uri, $params=array())
    {
        // parse the uri
        $parts = parse_url($uri);
        $path = (isset($parts['path'])) ? $parts['path'] : '';
        $query = (isset($parts['query'])) ? $parts['query'] : '';
        parse_str($query, $get_params);
        
        // add extra params
        $get_params = array_merge($get_params, $params);
        
        /*
            (PHP 5)
            http_build_query — Generate URL-encoded query string
        */
        return $path . '?' . http_build_query($get_params);
    }
    
    public function redirect($uri, $params=array(), $status=302, $raw=true)
    {
        if ( !headers_sent() )
        {
            if ($raw)  $uri = $this->baseUrl . $uri;
                
            if (!empty($params))
                $uri = $this->buildUri($uri, $params);
                
            if ( !$this->detect()->is_IIS && php_sapi_name() != 'cgi-fcgi' )
                $this->setStatusHeader( $status ); // This causes problems on IIS and some FastCGI setups

            header("Location:  $uri", true, $status);
            
            exit;
        }
    }
    
    // adapted from  WordPress
    public function detect()
    {
        static $obj = null;
        
        if ( !$obj )
        {
            // Simple browser detection
            $is_lynx = $is_gecko = $is_winIE = $is_macIE = $is_opera = $is_NS4 = $is_safari = $is_chrome = $is_iphone = false;

            if ( isset($_SERVER['HTTP_USER_AGENT']) ) {
                if ( strpos($_SERVER['HTTP_USER_AGENT'], 'Lynx') !== false ) {
                    $is_lynx = true;
                } elseif ( stripos($_SERVER['HTTP_USER_AGENT'], 'chrome') !== false ) {
                    if ( stripos( $_SERVER['HTTP_USER_AGENT'], 'chromeframe' ) !== false ) {
                        $is_chrome = true;
                        $is_winIE = ! $is_chrome;
                    } else {
                        $is_chrome = true;
                    }
                } elseif ( stripos($_SERVER['HTTP_USER_AGENT'], 'safari') !== false ) {
                    $is_safari = true;
                } elseif ( strpos($_SERVER['HTTP_USER_AGENT'], 'Gecko') !== false ) {
                    $is_gecko = true;
                } elseif ( strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false && strpos($_SERVER['HTTP_USER_AGENT'], 'Win') !== false ) {
                    $is_winIE = true;
                } elseif ( strpos($_SERVER['HTTP_USER_AGENT'], 'MSIE') !== false && strpos($_SERVER['HTTP_USER_AGENT'], 'Mac') !== false ) {
                    $is_macIE = true;
                } elseif ( strpos($_SERVER['HTTP_USER_AGENT'], 'Opera') !== false ) {
                    $is_opera = true;
                } elseif ( strpos($_SERVER['HTTP_USER_AGENT'], 'Nav') !== false && strpos($_SERVER['HTTP_USER_AGENT'], 'Mozilla/4.') !== false ) {
                    $is_NS4 = true;
                }
            }

            if ( $is_safari && stripos($_SERVER['HTTP_USER_AGENT'], 'mobile') !== false )
                $is_iphone = true;

            $is_IE = ( $is_macIE || $is_winIE );

            // Server detection

            /**
             * Whether the server software is Apache or something else
             * @global bool $is_apache
             */
            $is_apache = (strpos($_SERVER['SERVER_SOFTWARE'], 'Apache') !== false || strpos($_SERVER['SERVER_SOFTWARE'], 'LiteSpeed') !== false);

            /**
             * Whether the server software is IIS or something else
             * @global bool $is_IIS
             */
            $is_IIS = !$is_apache && (strpos($_SERVER['SERVER_SOFTWARE'], 'Microsoft-IIS') !== false || strpos($_SERVER['SERVER_SOFTWARE'], 'ExpressionDevServer') !== false);

            /**
             * Whether the server software is IIS 7.X
             * @global bool $is_iis7
             */
            $is_iis7 = $is_IIS && (strpos($_SERVER['SERVER_SOFTWARE'], 'Microsoft-IIS/7.') !== false);
            
            $obj = (object)compact('is_lynx', 'is_gecko', 'is_winIE', 'is_macIE', 'is_opera', 'is_NS4', 'is_safari', 'is_chrome', 'is_iphone', 'is_apache', 'is_IIS', 'is_iis7');
        }
        return $obj;
    }
    
    public function isRoute($route='/', $raw=true)
    {
        if ($raw) $route = $this->baseUrl . $route;
        return ( 0===strpos($this->get_request_uri(), $route) ) ? true : false;
    }
    
    public function isAjax()
    {
        // http://davidwalsh.name/detect-ajax
        // http://stackoverflow.com/questions/9828420/how-to-tell-if-a-page-is-being-called-via-ajax-or-on-its-own
        return (!empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest') ? true : false;
    }
    
    public function getVar($name, $default=false, $from='GET')
    {
        $var = $default;
        switch($from)
        {
            case 'POST':
                if (isset($_POST[$name]))
                    $var=$_POST[$name];
                break;
            case 'REQUEST':
                if (isset($_REQUEST[$name]))
                    $var=$_REQUEST[$name];
                break;
            case 'COOKIE':
                if (isset($_COOKIE[$name]))
                    $var=$_COOKIE[$name];
                break;
            case 'GET':
            default:
                if (isset($_GET[$name]))
                {
                    if (is_array($_GET[$name]))
                        $var = array_map('urldecode', $_GET[$name]);
                    else
                        $var = urldecode($_GET[$name]);
                }
                break;
        }
        return $var;
    }
    
    public function handle($uri = null, $method = null) 
    {
        $method = $this->get_request_method($method);
        $uri = $this->get_request_uri($uri);

        $routes = $this->routes[$method];
        if (empty($routes)) return false;

        foreach($routes as $route) 
        {
            $match_args = $this->matches($route, $uri);
            if(false === $match_args) continue;
            
            if(!is_callable($route['callback'])) throw new /*\*/RuntimeException('Uncallable callback provided for route: ' . $route['pattern']);
            return call_user_func_array($route['callback'], $match_args);
        }
        
        if (!empty($this->fallback['callback']) && is_callable($this->fallback['callback']))
        {
            return call_user_func_array($this->fallback['callback'], array());
        }
        return false;

    }


    private function matches($route, $uri) 
    {
        if($route['pattern'] === $this->baseUrl . '/')
        {
            return ($uri === $this->baseUrl . '/' || $uri === $this->baseUrl) ? array() : false;
        }

        list($pattern, $capture) = $this->expand_pattern($route);
        
        $count = preg_match($pattern, $uri, $matches);
        if($count === 0) return false;

        $args = array();
        foreach($capture as $offset) 
        {
            $args[] = isset($matches[$offset]) ? $matches[$offset] : null;
        }
        return $args;

    }



    private function expand_pattern($route) 
    {
        $input = $route['pattern'];

        $pattern = '';
        $parts = explode('/', trim($input, '/'));
        $optional = false;
        $bracket_count = 0;
        $capture_ints = array();

        foreach($parts as $part) 
        {
            $catch_all = (substr($part, 0, 4) === ':all');
            $capture   = (substr($part, 0, 1) === ':');
            $optional  = ($optional or substr($part, -1) === '?');
            $capture_i = null;

            // OR pattern
            if (preg_match(';^:\[([a-z0-9-_\|]+)\]\??$;i', $part, $m))
            {
                $orparts = array_filter(explode('|', $m[1]), 'strlen');
                $part = ':' . implode('|', $orparts) . '';
            }
            else
            {
                $part = strtr($part, array(
                    ':num' => ':[0-9]+',
                    ':any' => ':[a-z0-9-_]+',
                    ':all' => ':.*',
                ));
            }
            
            if($capture) 
            {
                $capture_i = $bracket_count + 1;
                $part = '(' . substr($part, 1) . ')';
                $bracket_count++;
            }

            if($optional) 
            {
                if($capture) $capture_i++;
                $part = "(/$part)?";
                $bracket_count++;
            } 
            else 
            {
                $part = "/$part";
            }

            $pattern .= $part;
            if($capture_i) $capture_ints[] = $capture_i;

            if($catch_all) break;

        }

        $pattern = ";^$pattern/?$;i";
        return array($pattern, $capture_ints);

    }

    public function getCurrentRequestUri()
    {
        return $this->get_request_uri();
    }
    
    private function get_request_uri($uri = null) 
    {
        if($uri === null) 
        {
            if (isset($_SERVER['PATH_INFO']))
            {
                $uri = $_SERVER['PATH_INFO'];
            }
            elseif (isset($_SERVER['REQUEST_URI']))
            {
                $uri = $_SERVER['REQUEST_URI'];
                $pos=strpos($uri, '?');
                if (false!==$pos) // strip query string
                    $uri = substr($uri, 0, $pos);
            }
            else
            {
                $uri = '';
            }
        }

        $uri = trim($uri, '/');
        return "/$uri";

    }

    private function get_request_method($method = null) 
    {
        if($method === null) 
        {
            $method = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : null;
        }

        $method = strtoupper($method);
        if(!in_array($method, self::$httpMethods)) $method = 'GET';

        if(
            $this->options['supportPost']
            and $method === 'POST'
            and isset($_POST['method'])
        ) 
        {
            $method = strtoupper($_POST['method']);
            if(!in_array($method, self::$methods)) $method = 'POST';
        }
        
        return $method;
    }
}