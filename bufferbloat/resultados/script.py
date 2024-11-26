import matplotlib.pyplot as plt

# Dados simulados para ilustrar
buffers = [20, 40, 80, 100]
rtt_normal = [20.367, 20.364, 20.322, 20.310]  # RTT médio no cenário normal
rtt_extremo = [120.8, 120.7, 120.6, 120.5]    # RTT médio no cenário extremo

# Gerar o gráfico comparativo
plt.figure(figsize=(10, 6))
plt.plot(buffers, rtt_normal, marker='o', label='Cenário Normal')
plt.plot(buffers, rtt_extremo, marker='s', label='Cenário Extremo')

# Configurações do gráfico
plt.title('Comparação do RTT Médio entre Cenários')
plt.xlabel('Tamanho do Buffer (pacotes)')
plt.ylabel('RTT Médio (ms)')
plt.xticks(buffers)
plt.legend()
plt.grid(True)

# Salvar o gráfico
plt.savefig('comparativo.png')
plt.show()
