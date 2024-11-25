from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
import time
import os

class BBTopo(Topo):
    """
    Topologia do experimento bufferbloat:
    - h1 conectado ao roteador com alta largura de banda (1 Gbps).
    - h2 conectado ao roteador com largura de banda limitada (1.5 Mbps).
    - RTT mínimo de 20 ms entre h1 e h2.
    - Buffer do roteador configurado para 100 pacotes.
    """
    def build(self):
        # Adicionando hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        # Adicionando roteador (como switch)
        router = self.addSwitch('s1')

        # Link rápido entre h1 e o roteador
        self.addLink(h1, router, bw=1000)

        # Link lento entre roteador e h2 com r2q ajustado
        self.addLink(router, h2, bw=1.5, delay='10ms', max_queue_size=100, use_htb=True, r2q=10)

def start_webserver(host):
    """
    Inicia um servidor web em um host.
    """
    print("Iniciando servidor web em", host)
    host.cmd('python3 -m http.server 80 &')

def stop_webserver():
    """
    Para qualquer servidor web que esteja rodando.
    """
    os.system('pkill -f "python3 -m http.server"')

if __name__ == '__main__':
    import argparse

    # Argumentos para configurar o experimento
    parser = argparse.ArgumentParser(description="Bufferbloat experiment")
    parser.add_argument('--queue', type=int, required=True, help="Tamanho do buffer (em pacotes)")
    parser.add_argument('--bw', type=float, required=True, help="Largura de banda do link lento (em Mbps)")
    parser.add_argument('--delay', type=str, required=True, help="Atraso do link (em ms)")
    parser.add_argument('--time', type=int, default=30, help="Tempo de duração do experimento (em segundos)")
    parser.add_argument('--output', type=str, required=True, help="Diretório para salvar os resultados")
    args = parser.parse_args()

    # Criar rede com a topologia personalizada
    topo = BBTopo()
    net = Mininet(topo=topo, link=TCLink, controller=Controller)
    net.start()

    print("*** Rede iniciada. Testando conectividade...")
    net.pingAll()

    # Obter hosts
    h1 = net.get('h1')
    h2 = net.get('h2')

    # Iniciar servidor web no h1
    start_webserver(h1)

    # Iniciar sequência de pings para medir RTT
    print("*** Iniciando sequência de pings para medir RTT...")
    ping_count = min(args.time * 10, 100)  # Limita para no máximo 100 pings
    ping_result = h1.cmd(f"ping -c {ping_count} 10.0.0.2 > {args.output}/ping.txt")
    print("*** Sequência de pings concluída.")

    # Monitoramento do tamanho da fila
    print("*** Iniciando monitoramento do tamanho da fila...")
    monitor_cmd = f"tc -s qdisc show dev s1-eth2 | grep backlog > {args.output}/q.txt"
    os.system(monitor_cmd)

    # Finalizar servidor web
    stop_webserver()
    print("*** Experimento concluído. Resultados salvos em:", args.output)

    # CLI para interagir manualmente
    CLI(net)

    # Finalizar rede
    net.stop()
