# DVWA: Command Injection

## Low

### 源代码

```php
<?php

if( isset( $_POST[ 'Submit' ]  ) ) {
    // Get input
    $target = $_REQUEST[ 'ip' ];

    // Determine OS and execute the ping command.
    if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
        // Windows
        $cmd = shell_exec( 'ping  ' . $target );
    }
    else {
        // *Unix
        $cmd = shell_exec( 'ping  -c 4 ' . $target );
    }

    // Feedback for the end user
    echo "<pre>{$cmd}</pre>";
}

?>
```

### 漏洞利用

直接尝试ping

![image-20220427094004100](./Lab2_Command_Injection.assets/image-20220427094004100.png)



尝试添加连接符  127.0.0.1 & ipconfig

![image-20220427093947695](./Lab2_Command_Injection.assets/image-20220427093947695.png)



查看PC用户

![image-20220427094106559](./Lab2_Command_Injection.assets/image-20220427094106559.png)



尝试添加用户，通过火绒提示可知，命令在无防火墙/安全软件的情况下，可正常执行 ~~（我就懒得允许了，建了还得自己再去删）~~

![image-20220427094404025](./Lab2_Command_Injection.assets/image-20220427094404025.png)



## Medium

### 源代码

```php
<?php

if( isset( $_POST[ 'Submit' ]  ) ) {
    // Get input
    $target = $_REQUEST[ 'ip' ];

    // Set blacklist
    $substitutions = array(
        '&&' => '',
        ';'  => '',
    );

    // Remove any of the charactars in the array (blacklist).
    $target = str_replace( array_keys( $substitutions ), $substitutions, $target );

    // Determine OS and execute the ping command.
    if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
        // Windows
        $cmd = shell_exec( 'ping  ' . $target );
    }
    else {
        // *nix
        $cmd = shell_exec( 'ping  -c 4 ' . $target );
    }

    // Feedback for the end user
    echo "<pre>{$cmd}</pre>";
}

?>
```

### 代码分析

可以看到，medium级别的代码在low级别的代码上增加量了对 && 和 ；的过滤，但并未过滤&，|，|| 。

### 漏洞利用

故上述Net user命令在此等级依然可正常实现。

![image-20220427094747936](./Lab2_Command_Injection.assets/image-20220427094747936.png)



## High

### 源代码

```php
<?php

if( isset( $_POST[ 'Submit' ]  ) ) {
    // Get input
    $target = trim($_REQUEST[ 'ip' ]);

    // Set blacklist
    $substitutions = array(
        '&'  => '',
        ';'  => '',
        '| ' => '',
        '-'  => '',
        '$'  => '',
        '('  => '',
        ')'  => '',
        '`'  => '',
        '||' => '',
    );

    // Remove any of the charactars in the array (blacklist).
    $target = str_replace( array_keys( $substitutions ), $substitutions, $target );

    // Determine OS and execute the ping command.
    if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
        // Windows
        $cmd = shell_exec( 'ping  ' . $target );
    }
    else {
        // *nix
        $cmd = shell_exec( 'ping  -c 4 ' . $target );
    }

    // Feedback for the end user
    echo "<pre>{$cmd}</pre>";
}

?>
```

### 代码分析

查看过滤代码发现 ”|”后面有个空格，因此当输入”127.0.0.1  |net view”，一样可以攻击，”|”是管道符，意思是将前者处理后的结果作为参数传给后者。

### 漏洞利用

稍作修改，上述Net user命令在此等级依然可正常实现。

![image-20220427095356516](./Lab2_Command_Injection.assets/image-20220427095356516.png)



## Impossible

### 源代码

```php
<?php

if( isset( $_POST[ 'Submit' ]  ) ) {
    // Check Anti-CSRF token
    checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );

    // Get input
    $target = $_REQUEST[ 'ip' ];
    $target = stripslashes( $target );

    // Split the IP into 4 octects
    $octet = explode( ".", $target );

    // Check IF each octet is an integer
    if( ( is_numeric( $octet[0] ) ) && ( is_numeric( $octet[1] ) ) && ( is_numeric( $octet[2] ) ) && ( is_numeric( $octet[3] ) ) && ( sizeof( $octet ) == 4 ) ) {
        // If all 4 octets are int's put the IP back together.
        $target = $octet[0] . '.' . $octet[1] . '.' . $octet[2] . '.' . $octet[3];

        // Determine OS and execute the ping command.
        if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
            // Windows
            $cmd = shell_exec( 'ping  ' . $target );
        }
        else {
            // *nix
            $cmd = shell_exec( 'ping  -c 4 ' . $target );
        }

        // Feedback for the end user
        echo "<pre>{$cmd}</pre>";
    }
    else {
        // Ops. Let the user name theres a mistake
        echo '<pre>ERROR: You have entered an invalid IP.</pre>';
    }
}

// Generate Anti-CSRF token
generateSessionToken();

?>
```

### 代码分析

stripslashes(string) : 该函数会删除字符串string中的反斜杠，返回已剥离反斜杠的字符串。

explode(separator,string,limit): 该函数把字符串打散为数组，返回字符串的数组。参数separator规定在哪里分割字符串，参数string是要分割的字符串，可选参数limit规定所返回的数组元素的数目。

is_numeric(string): 该检测string是否为数字或数字字符串，如果是返回TRUE，否则返回FALSE。

可以看到，Impossible级别的代码加入了Anti-CSRF token，同时对参数ip进行了严格的限制，只有诸如“数字.数字.数字.数字”的输入才会被接收执行，因此不存在命令注入漏洞。



## 常见问题

**中文乱码**

![image-20220427092749348](./Lab2_Command_Injection.assets/image-20220427092749348.png)

解决方案：更改dvwaPage.inc.php， main HTML code下的字符编码，将 UTF-8 改为 GB2312

![image-20220427092844009](./Lab2_Command_Injection.assets/image-20220427092844009.png)

