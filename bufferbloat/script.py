import re
import matplotlib.pyplot as plt

def parse_queue_file(file_path):
    """
    Lê os valores de backlog do arquivo q.txt.
    """
    queue_values = []
    with open(file_path, 'r') as f:
        for line in f:
            match = re.search(r'backlog\s(\d+)b', line)
            if match:
                queue_values.append(int(match.group(1)))
    return queue_values

def plot_queue(queue_values, output_path, title):
    """
    Plota o gráfico do tamanho da fila ao longo do tempo.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(queue_values, marker='o', linestyle='-', label='Tamanho da Fila')
    plt.title(title)
    plt.xlabel('Tempo (amostras)')
    plt.ylabel('Tamanho da Fila (bytes)')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

if __name__ == "__main__":
    buffer_sizes = [20, 40, 80, 100]
    base_dir = "resultados"

    for buffer_size in buffer_sizes:
        q_file_path = f"{base_dir}/bb-q{buffer_size}/q.txt"
        output_plot_path = f"{base_dir}/bb-q{buffer_size}/reno-buffer-q{buffer_size}.png"
        title = f"Tamanho da Fila para Buffer {buffer_size}"

        queue_values = parse_queue_file(q_file_path)
        plot_queue(queue_values, output_plot_path, title)
