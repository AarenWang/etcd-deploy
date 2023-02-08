
# etcd集群自动化部署
etcd集群部署涉及到证书生成和推送、etcd节点配置生成和推送,etcd配置文件维护等工作。本文记录下我自己搭建etcd集群工作过程为提高效率介绍出错
写的一些自动化脚本

按照etcd官方设计，etcd集群成员节点发现三种方式
- 静态成员
- etcd服务发现
- DNS发现etcd节点
他们有各自的优缺点，根据目前我们项目和环境情况，我选择了"方式一静态成员"。出于安全性考虑我们启用etcd client证书和 etcd peer证书



## 机器准备
在公有云上申请三个带公网的节点
| etcd节点名称  | 私有IP   |    公网IP  |
| -----  | ----    |   ---   |
| infra0  | 172.19.56.72    |  公网IP1   |
| infra0  | 172.19.56.71    |  公网IP2   |
| infra0  | 172.19.56.73    |  公网IP3   |


为方便后续操作，我们将IP地址导入到环境变量
```shell
export PRI_IP0="172.19.56.72"
export PUB_IP0="公网IP1"

export PRI_IP1="172.19.56.71"
export PUB_IP1="公网IP2"

export PRI_IP2="172.19.56.73"
export PUB_IP2="公网IP3"
```

云服务器ssh登录采用密钥方式，云服务器密钥本地存储路径 `$HOME/certs/etcd-temp.pem`

比如可以通过以下ssh登录到第一台服务器上  `ssh -i ~/certs/etcd-temp.pem root@$PUB_IP0`


## 生成证书 发布到etcd服务器上
一 证书生成工具选择
目前涉及密码学PKI(公钥基础设施)使用最广泛的是```openssl```,Cloudflare公司开源的cfssl[链接](https://github.com/cloudflare/cfssl)密码学和PKI工具箱也不错，能让证书生成过程简化一些，我们本次证书生成就用cfssl这个工具箱

etcd代码仓库里有使用cfssl生成证书的[例子](https://github.com/etcd-io/etcd/tree/main/hack/tls-setup),我做了一些改造[链接](https://github.com/AarenWang/etcd-deploy/tree/master/tls-setup)

二  安装cfssl命令行工具
```shell
go install  github.com/cloudflare/cfssl/cmd/cfssl@latest
go install  github.com/cloudflare/cfssl/cmd/cfssljson@latest
go install  github.com/mattn/goreman@latest
```

三 使用工具生成证书
git clone我们的[代码仓库](https://github.com/AarenWang/etcd-deploy)，然后修改tls-setup/config/req-csr.json，设置节点IP。
其它两个配置文件，自己根据需求可以做调整，不做修改，默认也是可以的


```shell
# 需要导入下环境变量，设置节点infra0到infra2对应的私有IP
export infra0=$PRI_IP0
export infra1=$PRI_IP1
export infra2=$PRI_IP2

# 进入tls-setup
cd tls-setup

# 生成证书
make all
#client证书在certs，peer证书再peer-certs目录下
# make 其它目标任务
# make clean ：清理证书,
# make ca :生成client CA证书
# make peerca  ：生成peer CA证书
# make req  :生成client证书
# make peerreq  :生成peer 节点证书
# 推送证书 IP按infra0、 infra1、infra2以此类推命名
# 证书名称以私有IP命名，推送通过公网IP，因此参数"私有IP:公网IP", IP对的形式

```

每个节点都有6个文件，三个节点，需要推送18个文件，写了个python脚本来推送
```shell
# 推送证书到目标机器
python3 etcd_cert_push.py  -l $PRI_IP0:$PUB_IP0,$PRI_IP1:$PUB_IP1,$PRI_IP2:$PUB_IP2
```

##  发布etcd和etcdctl二进制文件

去 etcd仓[库release页面](https://github.com/etcd-io/etcd/releases)  页面下载最新etcd包，我下载的是etcd-v3.4.23-linux-amd64.tar.gz。

etcd-v3.4.23-linux-amd64.tar.gz 本地解压，将etcd和etcdctl两个二进制文件发布到目标机器


```shell
# etcd和etcdctl二进制文件发布到第一台机器
scp -i certs/etcd-temp.pem ~/Downloads/etcd-v3.4.23-linux-amd64/etcd   root@$PUB_IP0:/usr/local/bin/
scp -i certs/etcd-temp.pem ~/Downloads/etcd-v3.4.23-linux-amd64/etcdctl   root@$PUB_IP0:/usr/local/bin/

# 第二台和第三台 省略
```


## 启动etcd集群节点验证
etcd集群节点启动过程需要设置大量参数，可以通过两种方式
- 方式一，命令行参数
- 方式二、指定配置文件
- 方式三、指定环境变量
本次 我们先生成命令行参数进行启动，验证没问题了，再生成配置文件，用指定配置文件方式启动
完整的参数列表可以参考etcd文档[链接](https://etcd.io/docs/v3.5/op-guide/configuration/)


一  生成启动命令参数
启动命令生成，etcd_start_cmd.py文件里 

``` python3 etcd_start_cmd.py -l $PRI_IP0,$PRI_IP0,$PRI_IP0  ```

生成IP：172.19.56.72,infra0 的etcd启动命令如下:
```
  etcd --name infra0 --initial-advertise-peer-urls https://172.19.56.72:2380 \
  --listen-peer-urls https://172.19.56.72:2380 \
  --listen-client-urls https://172.19.56.72:2379,https://127.0.0.1:2379 \
  --advertise-client-urls https://172.19.56.72:2379 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster infra0=https://172.19.56.72:2380,infra1=https://172.19.56.72:2380,infra2=https://172.19.56.72:2380 \
  --initial-cluster-state new \
  --client-cert-auth --trusted-ca-file=/etc/etcd/certs/ca-client.crt \
  --cert-file=/etc/etcd/certs/infra0-client.crt --key-file=/etc/etcd/certs/infra0-client.key \
  --peer-client-cert-auth --peer-trusted-ca-file=/etc/etcd/certs/peer-ca.crt \
  --peer-cert-file=/etc/etcd/certs/peer-infra0.crt --peer-key-file=/etc/etcd/certs/peer-infra0.key
  ```

 在三个节点上执行生成的启动命令，观察日志，是否有启动报错，如果没有报错，则执行etcdctl验证
 ```shell
 # 用私有IP访问验证
etcdctl \
 --cacert=/etc/etcd/certs/ca-client.crt \
 --cert=/etc/etcd/certs/infra0-client.crt \
 --key=/etc/etcd/certs/infra0-client.key \
 --endpoints=https://$PRI_IP0:2379 \
 put Name Jack

#用127.0.0.1验证
etcdctl \
 --cacert=/etc/etcd/certs/ca-client.crt \
 --cert=/etc/etcd/certs/infra0-client.crt \
 --key=/etc/etcd/certs/infra0-client.key \
 --endpoints=https://127.0.0.1:2379 \
 put Name Jack


# 验证etcd集群成员
etcdctl \
 --cacert=/etc/etcd/certs/ca-client.crt \
 --cert=/etc/etcd/certs/infra0-client.crt \
 --key=/etc/etcd/certs/infra0-client.key \
 --endpoints=https://$PRI_IP0:2379 \
 member list

 ```


## 生成etcd配置文件
以上验证通过后，最好将etcd启动参数放到yaml配置文件里。etcd通过指定yaml配置文件启动
生成配置文件脚本是 ```etcd_cfg_gen.py```

```shell
#生成配置文件
python3 etcd_cfg_gen.py -l $PRI_IP0,$PRI_IP1,$PRI_IP2

#在当前目录下生成 etcd-$IP.yaml配置文件

# 推送文件到etcd服务器上
scp -i ~/certs/etcd-temp.pem  etcd-$PRI_IP0.yaml  root@$PUB_IP0:/etc/etcd/etcd.yaml
scp -i ~/certs/etcd-temp.pem  etcd-$PRI_IP1.yaml  root@$PUB_IP1:/etc/etcd/etcd.yaml
scp -i ~/certs/etcd-temp.pem  etcd-$PRI_IP2.yaml  root@$PUB_IP2:/etc/etcd/etcd.yaml
```

在三台etcd机器上,使用配置文件启动验证
```shell
etcd --config-file  /etc/etcd/etcd.yaml
```

## 附加 etcd配置说明
完整的参数列表可以参考etcd文档[链接](https://etcd.io/docs/v3.5/op-guide/configuration/)

```
--name：方便理解的节点名称，默认为 default，在集群中应该保持唯一
--data-dir：服务运行数据保存的路径，默认为 ${name}.etcd
--snapshot-count：指定有多少事务（transaction）被提交时，触发截取快照保存到磁盘
--heartbeat-interval：leader 多久发送一次心跳到 followers。默认值是 100ms
--eletion-timeout：重新投票的超时时间，如果follower在该时间间隔没有收到心跳包，会触发重新投票，默认为 1000 ms
--listen-peer-urls：和同伴通信的地址，比如 http://ip:2380，如果有多个，使用逗号分隔。需要所有节点都能够访问，所以不要使用 localhost
--advertise-client-urls：对外公告的该节点客户端监听地址，这个值会告诉集群中其他节点
--listen-client-urls：对外提供服务的地址：比如 http://ip:2379,http://127.0.0.1:2379，客户端会连接到这里和etcd交互
--initial-advertise-peer-urls：该节点同伴监听地址，这个值会告诉集群中其他节点
--initial-cluster：集群中所有节点的信息，格式为 node1=http://ip1:2380,node2=http://ip2:2380,…。需要注意的是，这里的 node1 是节点的--name指定的名字；后面的ip1:2380 是--initial-advertise-peer-urls 指定的值
--initial-cluster-state：新建集群的时候，这个值为 new；假如已经存在的集群，这个值为existing
--initial-cluster-token：创建集群的token，这个值每个集群保持唯一。这样的话，如果你要重新创建集群，即使配置和之前一样，也会再次生成新的集群和节点 uuid；否则会导致多个集群之间的冲突，造成未知的错误

　　所有以--init开头的配置都是在第一次启动etcd集群的时候才会用到，后续节点的重启会被忽略，如--initial-cluseter参数。所以当成功初始化了一个etcd集群以后，就不再需要这个参数或环境变量了。
如果服务已经运行过就要把修改 --initial-cluster-state 为existing


--client-cert-auth  client端请求是否启用认证  
--trusted-ca-file=/etc/etcd/certs/ca-client.crt  client CA证书
--cert-file=/etc/etcd/certs/infra0-client.crt   client证书
--key-file=/etc/etcd/certs/infra0-client.key  client 证书密钥
--peer-client-cert-auth  etcd集群成员peer通信是否启用认证
--peer-trusted-ca-file=/etc/etcd/certs/peer-ca.crt   peer CA证书
--peer-cert-file=/etc/etcd/certs/peer-infra0.crt    peer节点证书
--peer-key-file=/etc/etcd/certs/peer-infra0.key   peer节点证书密钥
　　
```