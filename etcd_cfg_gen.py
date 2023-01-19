
import yaml
import os
import sys
import argparse


def generate_etc_cfg(yaml_file,i,pri_ip,pri_ip_list): 
    py_object = {}
    py_object['name'] = 'infra'+str(i)
    py_object['data-dir'] = '/var/lib/etcd'
    py_object['initial-advertise-peer-urls'] = 'https://'+pri_ip+':2380'
    py_object['listen-peer-urls'] = 'https://'+pri_ip+':2380'
    py_object['listen-client-urls'] = 'https://'+pri_ip+':2379,https://127.0.0.1:2379'
    py_object['advertise-client-urls'] = 'https://'+pri_ip+':2379'
    py_object['initial-cluster-token'] = 'etcd-cluster-1'
    py_object['initial-cluster'] = 'infra0=https://'+pri_ip_list[0]+':2380,infra1=https://'+pri_ip_list[1]+':2380,infra2=https://'+pri_ip_list[2]+':2380'
    py_object['initial-cluster-state'] = 'new'
  
    client_transport_security = {}
    client_transport_security['cert-file'] = '/etc/etcd/certs/infra'+str(i)+'-client.crt'
    client_transport_security['key-file'] =  '/etc/etcd/certs/infra'+str(i)+'-client.key'
    client_transport_security['trusted-ca-file'] = '/etc/etcd/certs/ca-client.crt'
    client_transport_security['client-cert-auth'] = 'true'
    py_object['client-transport-security'] = client_transport_security

    peer_transport_security = {}
    peer_transport_security['cert-file'] = '/etc/etcd/certs/peer-infra'+str(i)+'.crt'
    peer_transport_security['key-file'] =  '/etc/etcd/certs/peer-infra'+str(i)+'.key'
    peer_transport_security['trusted-ca-file'] = '/etc/etcd/certs/peer-ca.crt'
    peer_transport_security['client-cert-auth'] = 'true'
    py_object['peer-transport-security'] = peer_transport_security

    file = open(yaml_file, 'w', encoding='utf-8')
    stream = yaml.dump(py_object)
    stream = stream.replace('\'true\'','true')
    file.write(stream)
    #yaml.safe_dump(py_object, sys.stdout, default_flow_style=False)

    file.close()



if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog = "生成etcd配置文件",description = "etcd不同节点启动配置文件",epilog = "")
  parser.add_argument("-l", "--ip_list",help="指定IP列表，多个IP地址用逗号分隔",required=True) 
  args = parser.parse_args()
  args.ip_list = args.ip_list.split(",")
  print("输入IP列表为："+str(args.ip_list))
  i = 0
  for ip in args.ip_list:
    print("生成IP："+ip+",infra"+str(i)+ " 的etcd配置文件")
    generate_etc_cfg("etcd-"+ip+".yaml",i,ip,args.ip_list)
    i = i + 1
  
  