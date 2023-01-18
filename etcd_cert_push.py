import argparse
import os

mkdir_cmd = "[ -d /etc/etcd/certs ] || mkdir -p /etc/etcd/certs"
cert_dir = "/etc/etcd/certs/"
ssh_exec_cmd = "ssh -i %s root@%s \"%s\""
ssh_pem_path = "~/certs/etcd-temp.pem"
local_cert_path = "tls-setup/"

def ssh_exec(key_file,ip, cmd):
    print("执行命令："+cmd)
    ssh_cmd = ssh_exec_cmd % (key_file, ip, cmd)
    print("执行命令："+ssh_cmd)
    os.system(ssh_cmd)

def push_cert(key_file,ip, src_file,dest_file):
    print("推送文件："+local_cert_path+src_file+" 到 "+ip+":"+cert_dir+dest_file)
    scp_cmd = "scp -i %s %s root@%s:/etc/etcd/certs/%s" % (key_file, local_cert_path+src_file, ip,dest_file)  
    os.system(scp_cmd)


if __name__ == "__main__":

  parser = argparse.ArgumentParser(prog = "推送etcd证书",description = "推送etcd集群节点证书到对应目标节点",epilog = "")
  parser.add_argument("-l", "--ip_list",help="指定私有IP:公网IP列表，多个私有IP:公网IP用逗号分隔,比如 192.168.3.2:公网IP1,192.168.3.3:公网IP2 ",required=True) 
  args = parser.parse_args()
  args.ip_list = args.ip_list.split(",")
  print("输入IP列表为："+str(args.ip_list))
  for ip_pair in args.ip_list:
    ip = ip_pair.split(":")[1]
    ssh_exec(ssh_pem_path,ip, mkdir_cmd)

  i = 0
  ip_pair_list = args.ip_list
  for ip_pair in ip_pair_list:
      pri_ip =  ip_pair.split(":")[0]
      pub_ip =  ip_pair.split(":")[1]
      print("推送文件："+pub_ip+" 到 "+pri_ip+":"+cert_dir)
      push_cert(ssh_pem_path,pub_ip, "certs/ca.pem","ca-client.crt")
      push_cert(ssh_pem_path,pub_ip, "peer-certs/"+pri_ip+".pem","infra"+str(i)+"-client.crt")
      push_cert(ssh_pem_path,pub_ip, "peer-certs/"+pri_ip+"-key.pem","infra"+str(i)+"-client.key")

      push_cert(ssh_pem_path,pub_ip, "peer-certs/ca.pem","peer-ca.crt")
      push_cert(ssh_pem_path,pub_ip, "peer-certs/"+pri_ip+".pem","peer-infra"+str(i)+".crt")
      push_cert(ssh_pem_path,pub_ip, "peer-certs/"+pri_ip+"-key.pem","peer-infra"+str(i)+".key")
      i = i + 1
      

