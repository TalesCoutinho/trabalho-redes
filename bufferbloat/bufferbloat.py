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
    # Parâmetros para resultados extremos
    queue_sizes = [20, 40, 80, 100]
    bw = 0.1  # Largura de banda fixa em 0.1 Mbps
    delay = "100ms"  # Atraso fixo de 100 ms
    time_duration = 30  # Duração do experimento em segundos
    output_base_dir = "resultados_extremos"

    # Criar pasta principal para resultados
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    for queue_size in queue_sizes:
        output_dir = f"{output_base_dir}/bb-q{queue_size}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"*** Executando experimento para tamanho de fila {queue_size}...")

        # Criar topologia e iniciar rede
        topo = BBTopo(bw=bw, delay=delay, queue_size=queue_size)
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
        ping_count = min(time_duration * 10, 100)  # Limita para no máximo 100 pings
        h1.cmd(f"ping -c {ping_count} 10.0.0.2 > {output_dir}/ping.txt")
        print("*** Sequência de pings concluída.")

        # Monitorar backlog
        print("*** Iniciando monitoramento do tamanho da fila...")
        with open(f"{output_dir}/q.txt", 'w') as f:
            for _ in range(time_duration * 10):  # Monitorar por toda a duração do experimento
                monitor_cmd = "tc -s qdisc show dev s1-eth2 | grep backlog"
                output = os.popen(monitor_cmd).read().strip()
                backlog_value = parse_backlog(output)
                f.write(f"{backlog_value}\n")
                time.sleep(0.1)

        print(f"*** Experimento para fila {queue_size} concluído. Resultados salvos em {output_dir}")

        # Finalizar rede
        net.stop()
