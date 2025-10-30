# Explorador de Dimensões - Rick and Morty

Este é um projeto em Python que traz para você uma experiência visual e interativa no universo multiversal da série animada Rick and Morty.

## Descrição

O script `explorador_dimensoes.py` utiliza a API oficial do Rick and Morty para buscar informações detalhadas sobre as várias dimensões, locais e os personagens residentes em cada uma delas. Com uma interface gráfica responsiva desenvolvida com `tkinter` e o moderno `ttkbootstrap`, você pode explorar:

- A lista completa de dimensões e locais do multiverso de Rick and Morty;
- Filtrar e buscar localizações por nome, tipo ou dimensão;
- Visualizar detalhes completos de cada local, incluindo seu tipo, dimensão, número de residentes e ID;
- Conhecer os personagens residentes em cada dimensão, com fotos e informações básicas exibidas em cards dinâmicos;
- Estatísticas gerais do multiverso, mostrando quantas localizações e residentes foram carregados, o tipo e a dimensão mais comuns, e a localização mais populosa.

## Funcionalidades Técnicas

- Consumo da API oficial Rick and Morty (https://rickandmortyapi.com/api) para obtenção dos dados em tempo real;
- Carregamento assíncrono de dados e imagens usando `threading` para não travar a interface;
- Interface construída com `tkinter` utilizando `ttkbootstrap` para um visual moderno e responsivo;
- Exibição de imagens dos personagens usando `PIL` (Pillow);
- Uso de widgets como `Treeview`, `ScrolledText`, `Canvas` e botões para navegação e interação intuitiva.

## Requisitos

- Python 3.10 ou superior
- Bibliotecas Python:
  - requests
  - tkinter (incluído no Python)
  - ttkbootstrap
  - Pillow

Instale as dependências com:
```
pip install requests ttkbootstrap Pillow
```

## Como usar

1. Clone ou baixe este repositório.
2. Execute o arquivo `explorador_dimensoes.py` com Python:
```
python explorador_dimensoes.py
```
3. A interface abrirá e começará a carregar as localizações do multiverso.
4. Use a busca para filtrar localizações, clique nas localizações para ver detalhes.
5. Explore os residentes das dimensões e suas informações visuais.
6. Aproveite as estatísticas gerais para um panorama do multiverso.

## Sobre o Multiverso de Rick and Morty

Na série, o multiverso consiste em infinitas dimensões paralelas onde as histórias e personagens variam. Cada decisão cria ramificações, gerando realidades alternativas únicas. Este projeto captura essa riqueza oferecendo acesso a dados reais da API oficial, tornando possível navegar e entender melhor a complexidade desse universo.

---

Desenvolvido como um projeto pessoal para aprender integração com APIs, interfaces gráficas e manipulação assíncrona em Python, além de uma homenagem ao fascinante universo de Rick and Morty.
