from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

from monitor import monitor_qlen

import sys
import os
import math

parser = ArgumentParser(description="Bufferbloat tests")
parser.add_argument('--bw-host', '-B',
                    type=float,
                    help="Bandwidth of host links (Mb/s)",
                    default=1000)

parser.add_argument('--bw-net', '-b',
                    type=float,
                    help="Bandwidth of bottleneck (network) link (Mb/s)",
                    required=True)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    required=True)

parser.add_argument('--time', '-t',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of network interface in packets",
                    default=100)

# Linux uses CUBIC-TCP by default that doesn't have the usual sawtooth
# behaviour.  For those who are curious, invoke this script with
# --cong cubic and see what happens...
# sysctl -a | grep cong should list some interesting parameters.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="reno")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
    "Simple topology for bufferbloat experiment."

    def build(self, n=2):
        # Adicionando hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Here I have created a switch.  If you change its name, its
        # interface names will change from s0-eth1 to newname-eth1.
        router = self.addSwitch('s0')

        # Link rápido entre h1 e o roteador
        self.addLink(h1, router, bw=args.bw_host, delay='0ms', use_htb=True)

        # Link lento entre o roteador e h2
        self.addLink(router, h2, bw=args.bw_net, delay=f'{args.delay}ms', max_queue_size=args.maxq, use_htb=True)

# Simple wrappers around monitoring utilities.  You are welcome to
# contribute neatly written (using classes) monitoring scripts for
# Mininet!

def start_iperf(net):
    if args.cong == "quic": 
        return
    h1 = net.get('h1')
    h2 = net.get('h2')
    print("Starting iperf server...")
    server = h2.popen("iperf -s -w 16m")

    print("Starting iperf client on h1...")
    client = h1.popen(f"iperf -c {h2.IP()} -t {args.time} -w 16m")

    return server, client
    
def start_qmon(iface, interval_sec=0.1, outfile="q.txt"):
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start()
    return monitor

def start_ping(net):
    h1 = net.get('h1')
    h2 = net.get('h2')

    print("Starting ping from h1 to h2...")
    h1.popen(f"ping -i 0.1 {h2.IP()} > {args.dir}/ping.txt", shell=True)

def start_webserver(net):
    if (args.cong == "quic"):
        return start_quic_server(net)

    h1 = net.get('h1')
    proc = h1.popen("python webserver.py", shell=True)
    sleep(1)
    return [proc]

def start_quic_server(net):
    h1 = net.get('h1')
    print("Starting QUIC webserver on h1...")
    proc = h1.popen(f"./.quiche/bin/quiche-server --listen {h1.IP()}:4433 --root . --cert cert.pem --key key.pem", shell=True)
    sleep(1)
    return [proc]

def measure_webpage_transfer(net):
    h2 = net.get('h2')
    fetch_times = []

    print("Measuring webpage...")
    time_left = args.time
    while time_left > 0:

        for _ in range(3):
            start_time = time()
            if args.cong == "quic":
                response = h2.cmd(f"./.quiche/bin/quiche-client --no-verify https://{net.get('h1').IP()}:4433/index.html")
            else:
                response = h2.cmd(f"curl -o /dev/null -s -w '%{{time_total}}\\n' {net.get('h1').IP()}/index.html")
            delta = time() - start_time

            fetch_times.append(delta)

            time_left -= delta

    return fetch_times

def bufferbloat():
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
    if args.cong != 'quic':
        os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    topo = BBTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    qmon = start_qmon(iface='s0-eth2', outfile='%s/q.txt' % (args.dir))

    start_iperf(net)
    start_ping(net)
    start_webserver(net)
    fetch_times = measure_webpage_transfer(net)

    qmon.terminate()
    net.stop()

    avg_time = sum(fetch_times) / len(fetch_times) * 1000
    std_dev = math.sqrt(sum((x - avg_time) ** 2 for x in fetch_times) / len(fetch_times)) * 1000
    
    avg = f"[{args.cong}-q{args.maxq}] Average fetch time : {avg_time:.2f}ms, Std Dev: {std_dev:.2f}ms"
    print(avg)
    os.system(f"echo '{avg}' >> {args.dir}/../curl_times.txt")
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()

if __name__ == "__main__":
    bufferbloat()
