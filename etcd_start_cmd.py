from string import Template
import argparse

CERT_DIR="/etc/etcd/certs"
ETCD_DATA_DIR="/var/lib/etcd"

def generate_etcd_start_command(cert_dir, infra_name, ip_infra, ip0, ip1, ip2):
  command = """
  etcd --name $infra_name --initial-advertise-peer-urls https://$ip:2380 \\
  --listen-peer-urls https://$ip:2380 \\
  --listen-client-urls https://$ip:2379,https://127.0.0.1:2379 \\
  --advertise-client-urls https://$ip:2379 \\
  --initial-cluster-token etcd-cluster-1 \\
  --initial-cluster infra0=https://$ip0:2380,infra1=https://$ip1:2380,infra2=https://$ip2:2380 \\
  --initial-cluster-state new \\
  --client-cert-auth --trusted-ca-file=$cert_dir/ca-client.crt \\
  --cert-file=$cert_dir/$infra_name-client.crt --key-file=$cert_dir/$infra_name-client.key \\
  --peer-client-cert-auth --peer-trusted-ca-file=$cert_dir/peer-ca.crt \\
  --peer-cert-file=$cert_dir/peer-$infra_name.crt --peer-key-file=$cert_dir/peer-$infra_name.key
  """
  #d = dict(cert_dir=cert_dir, infra_name=infra_name, ip=ip, ip0=ip0, ip1=ip1, ip2=ip2)
  d = {"cert_dir":cert_dir, "infra_name":infra_name, "ip":ip_infra, "ip0":ip0, "ip1":ip1, "ip2":ip2}
  return Template(command).substitute(d)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog = "生成etcd启动命令",description = "etcd不同节点启动命令生成",epilog = "")
  parser.add_argument("-l", "--ip_list",help="指定IP列表，多个IP地址用逗号分隔",required=True) 
  args = parser.parse_args()
  args.ip_list = args.ip_list.split(",")
  print("输入IP列表为："+str(args.ip_list))
  i = 0
  for ip in args.ip_list:
    print("生成IP："+ip+",infra"+str(i)+ " 的etcd启动命令")
    cmd = generate_etcd_start_command(CERT_DIR, "infra"+str(i), ip, args.ip_list[0], args.ip_list[1], args.ip_list[2])
    i = i + 1
    print(cmd)
  


