import matplotlib.pyplot as plt
import argparse

def col(n, data):
    """
    Retorna a coluna `n` dos dados, ignorando linhas inválidas.
    """
    for item in data:
        try:
            yield float(item[n])  # Converte para float
        except (IndexError, ValueError):
            continue

# Configuração de argumentos
parser = argparse.ArgumentParser(description="Plot Buffer Queue Length")
parser.add_argument("-f", "--file", required=True, help="Input file containing queue data")
parser.add_argument("-o", "--output", required=True, help="Output image file")
args = parser.parse_args()

# Ler arquivo de dados
with open(args.file) as f:
    data = [line.split() for line in f if line.strip()]  # Ignora linhas vazias

# Extração de valores
qlens = list(map(float, col(0, data)))  # Extraindo apenas a primeira coluna

# Gerar o gráfico
plt.plot(qlens)
plt.title("Tamanho da Fila (Buffer)")
plt.xlabel("Tempo (amostras)")
plt.ylabel("Tamanho da Fila (bytes)")
plt.grid()
plt.savefig(args.output)
plt.close()
