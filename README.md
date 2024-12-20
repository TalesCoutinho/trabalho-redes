Esse repositório contém scripts para executar experimentos de bufferbloat comparando TCP Reno, TCP BBR e QUIC. Para rodar o ambiente do mininet precisa estar configurado seguindo as intruções do próprio mininet em https://mininet.org/download/ .

## Execução
Para executar o código, utilize o script `run.sh`.  
Se nenhum argumento for passado, o script será executado para `qsize = 20`.  

Exemplos:
- Para `qsize = 20`:  
  ```bash
  ./run.sh
  ```
- Para múltiplos valores de qsize, como 20, 50 e 100


  ```bash
  ./run.sh 60 100
  ```
  
## Dependências
   - Mininet (instale seguindo as recomendações oficiais utilizando o script `install.sh` com a opção `-a`)
   - `curl` 
   - `python3-matplotlib`
