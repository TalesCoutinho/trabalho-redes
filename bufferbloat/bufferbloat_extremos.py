from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
import time
import os

class BBTopo(Topo):
    """
    Topologia do experimento bufferbloat:
    - h1 conectado ao roteador com alta largura de banda.
    - h2 conectado ao roteador com largura de banda limitada.
    """
    def build(self, bw, delay, queue_size):
        # Adicionando hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        # Adicionando roteador como switch
        router = self.addSwitch('s1')

        # Link rápido entre h1 e o roteador
        self.addLink(h1, router, bw=1000)

        # Link lento entre o roteador e h2
        self.addLink(router, h2, bw=bw, delay=delay, max_queue_size=queue_size, use_htb=True)

def parse_backlog(line):
    """
    Extrai os valores numéricos de backlog de uma linha do comando `tc`.
    """
    parts = line.split()
    if "backlog" in parts:
        try:
            return int(parts[parts.index("backlog") + 1].replace("b", ""))  # Extrai o valor numérico
        except (ValueError, IndexError):
            return 0
    return 0

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

    # Criar pasta de saída
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    print(f"*** Executando experimento para fila de tamanho {args.queue}...")

    # Criar rede com a topologia personalizada
    topo = BBTopo(bw=args.bw, delay=args.delay, queue_size=args.queue)
    net = Mininet(topo=topo, link=TCLink, controller=Controller)
    net.start()

    # Testar conectividade
    print("*** Testando conectividade...")
    net.pingAll()

    # Obter hosts
    h1 = net.get('h1')
    h2 = net.get('h2')

    # Iniciar sequência de pings para medir RTT
    print("*** Iniciando sequência de pings para medir RTT...")
    ping_count = min(args.time * 10, 100)  # Limita para no máximo 100 pings
    h1.cmd(f"ping -c {ping_count} 10.0.0.2 > {args.output}/ping.txt")
    print("*** Sequência de pings concluída.")

    # Monitorar backlog
    print("*** Iniciando monitoramento do tamanho da fila...")
    with open(f"{args.output}/q.txt", 'w') as f:
        for _ in range(args.time * 10):  # Monitorar por toda a duração do experimento
            monitor_cmd = "tc -s qdisc show dev s1-eth2 | grep backlog"
            output = os.popen(monitor_cmd).read().strip()
            backlog_value = parse_backlog(output)
            f.write(f"{backlog_value}\n")
            time.sleep(0.1)

    print(f"*** Experimento concluído. Resultados salvos em {args.output}")

    # Finalizar rede
    net.stop()
