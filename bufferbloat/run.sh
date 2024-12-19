#!/bin/bash
# Note: Mininet must be run as root. So invoke this shell script using sudo.

# Clear old results
rm -rf ../results  > /dev/null 2>&1 
sudo mn -c  > /dev/null 2>&1
sudo pkill quiche* > /dev/null 2>&1

time=90
bwnet=1.5
bwhost=1000
delay=10  # RTT total de 20ms -> 10ms em cada direção
iperf_port=5001

for cong in "reno" "bbr" "quic"; do
    for qsize in 20 "$@"; do
        dir=../results/resultado-$cong-q$qsize

        # Cria o diretório para armazenar os resultados
        mkdir -p $dir

        echo "Running bufferbloat.py with qsize=$qsize..."
        
        # Executa o experimento com os parâmetros especificados
        sudo python3 bufferbloat.py --bw-host $bwhost --bw-net $bwnet --delay $delay --dir $dir --time $time --maxq $qsize --cong $cong

        echo "Plotting results for qsize=$qsize..."

        # Gera os gráficos de ocupação de fila e RTT
        python3 plot_queue.py -f $dir/q.txt -o $dir/$cong-buffer-q$qsize.png
        python3 plot_ping.py -f $dir/ping.txt -o $dir/$cong-rtt-q$qsize.png
        sudo mn -c > /dev/null 2>&1
        echo "--- DONE! :-)"
    done
done
