import matplotlib.pyplot as plt

# Dados simulados para ilustrar
buffers = [20, 40, 80, 100]
queue_normal = [10, 15, 18, 20]  # Tamanho médio da fila no cenário normal
queue_extremo = [18, 30, 60, 80] # Tamanho médio da fila no cenário extremo

# Gerar o gráfico comparativo
plt.figure(figsize=(10, 6))
plt.plot(buffers, queue_normal, marker='o', label='Cenário Normal')
plt.plot(buffers, queue_extremo, marker='s', label='Cenário Extremo')

# Configurações do gráfico
plt.title('Comparação do Tamanho Médio da Fila entre Cenários')
plt.xlabel('Tamanho do Buffer (pacotes)')
plt.ylabel('Tamanho Médio da Fila (pacotes)')
plt.xticks(buffers)
plt.legend()
plt.grid(True)

# Salvar o gráfico
plt.savefig('queue-comparativo.png')
plt.show()
