# operation-tools
Some tools for operation writen by ningbo.

## mail-by-local

It is a project that can send email by localhost for linux.It functions are multi receivers,cc and attachment.

这个项目在linux下从本地发邮件，能够实现多个地址发送，抄送和附件功能，本人把它用在运维上。
### 说明

+ mail_by_local.py这个文件定义了功能，只需要引入这个文件的send_email函数。
+ 其他文件是我的功能文件，可以参考。

### 配置本地邮件服务过程
1. 配置网络
2. 安装yum install -y postfix
3. 配置
vi /etc/postfix/main.cf
在文件末尾添加：
myhostname = test.site
myorigin = $myhostname
inet_interfaces = $myhostname, localhost
inet_protocols = ipv4

修改完可以用postfix check检查

vi /etc/hosts
添加：
<yourip> linux-test.site

完成后：    
systemctl start postfix

启动后可以用postconf -n查看postfix现在生效的配置。


4.发送测试邮件
echo "1234" |mail -s "test" yangningbo@xxx.com

## data-flow-network

### 输入
1. 第一列：源节点
2. 第二列：目标节点
3. 第三列：筛选信息，这里是地区

### 功能
1. 节点可以输入汉字，节点颜色可以选择
2. 边上可以加入汉字
[图](https://github.com/yangningbo666/operation-tools/blob/master/data-flow-network/network.png)

