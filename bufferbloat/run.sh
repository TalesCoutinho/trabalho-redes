#!/bin/bash

# Parâmetros do experimento
queue_sizes=(20 40 80 100)
output_dir="resultados_extremos"

# Garantir que a pasta de saída exista
mkdir -p "$output_dir"

for qsize in "${queue_sizes[@]}"; do
    dir="$output_dir/bb-q$qsize"
    mkdir -p "$dir"

    echo "Executando experimento para fila $qsize..."

    # Executar o experimento com bufferbloat_extremos.py
    sudo python3 bufferbloat_extremos.py --queue "$qsize" --bw 0.1 --delay "100ms" --time 30 --output "$dir"

    echo "Gerando gráficos para fila $qsize..."

    # Gerar gráficos
    python3 plot_queue.py -f "$dir/q.txt" -o "$dir/reno-buffer-q$qsize.png"
    python3 plot_ping.py -f "$dir/ping.txt" -o "$dir/reno-rtt-q$qsize.png"
done

echo "Todos os experimentos concluídos. Resultados salvos em $output_dir."
