#!/bin/bash

# Note: Mininet must be run as root. Invoke this shell script using sudo.

time=90
bwnet=1.5
delay="10ms"  # Atraso por link (ida e volta soma 20ms)
iperf_port=5001

# Lista de tamanhos de buffer a testar
queue_sizes=(20 40 80 100)

for qsize in "${queue_sizes[@]}"; do
    dir=bb-q$qsize

    # Criar o diretório de saída se não existir
    mkdir -p $dir

    echo "Running experiment with queue size $qsize..."

    # Executar o bufferbloat.py
    sudo python3 bufferbloat.py --queue $qsize --bw $bwnet --delay $delay --time $time --output $dir

    echo "Experiment completed for queue size $qsize. Generating plots..."

    # Gerar gráfico de RTT
    python3 plot_ping.py -f $dir/ping.txt -o $dir/reno-rtt-q$qsize.png

    # Gerar gráfico do tamanho da fila
    python3 plot_queue.py -f $dir/q.txt -o $dir/reno-buffer-q$qsize.png

    echo "Plots generated for queue size $qsize:"
    echo "  RTT plot: $dir/reno-rtt-q$qsize.png"
    echo "  Buffer plot: $dir/reno-buffer-q$qsize.png"
done

echo "All experiments completed. Results stored in respective directories."
