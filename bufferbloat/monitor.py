import os
import time
import argparse

def monitor_queue(interface, output_file, interval):
    """
    Monitora o tamanho da fila (backlog) da interface especificada.
    """
    print(f"Monitorando a interface {interface}. Salvando em {output_file}")
    with open(output_file, 'w') as f:
        while True:
            try:
                cmd = f"tc -s qdisc show dev {interface} | grep backlog"
                result = os.popen(cmd).read()
                if result:
                    f.write(result + '\n')
                    f.flush()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("Monitoramento interrompido.")
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitoramento do tamanho da fila.")
    parser.add_argument('--interface', required=True, help="Interface a ser monitorada (ex.: s1-eth2)")
    parser.add_argument('--output', required=True, help="Arquivo de saída para salvar os dados")
    parser.add_argument('--interval', type=float, default=0.1, help="Intervalo entre medições (em segundos)")
    args = parser.parse_args()

    monitor_queue(args.interface, args.output, args.interval)
