## Visualizador Volumétrico

Esse software é um visualizador de dados volumétricos cujo principal objetivo é fornecer ao usuário a possibilidade de explorar o dado descobrindo como o volume se distribui em relação a densidade e também testar de forma simples diferentes funções de transferência.
<div style="text-align: center;">
<img src="images\transfer_function_view_small.png" alt="Lobster Render" width="800"  />
</div>

### Informações relevantes
* Desenvolvido em Python e GLSL
* Utiliza as bibliotecas: 
    * Numpy
    * Pyglm
    * DearPyGUI
    * PyOpenGL
    * Glfw
    * Pynrrd
    * Pytest
    * Ruff
* Volumes suportados: .raw, .nhdr
* Funções de transferência suportadas: 1D linear .tfl

### Pré-requisitos

Esse projeto utiliza o uv para gerenciamento de pacotes e é necessário instalá-lo caso já não o tenha feito. Para instalar o uv, você pode seguir a opção mais apropriada para você no guia oficial de instalação: https://docs.astral.sh/uv/getting-started/installation/

### Preparando o ambiente

Após clonar o repositório, navegar até a pasta ..\volumetric-viewer\volumetric-viewer.
Com a pasta aberta no terminal, você deve executar o seguinte comando:

```
uv sync
```

Esse comando vai criar um ambiente virtual, instalando todas as dependências necessárias tanto para desenvolvimento quanto para a execução do software, incluindo a versão do Python a ser utilizada.

### Rodando o visualizador

E para executar o programa, após a instalação das dependências, rode:

```
uv run volumetric-viewer
```
Caso ocorra algum erro, verifique se está na pasta correta (..\volumetric-viewer\volumetric-viewer).

### Ferramentas para desenvolvedores

Nesse projeto, foram utilizadas algumas ferramentas para auxiliar no processo de desenvolvimento. Para utilizá-las, basta rodar os comandos a seguir:

#### Pytest

Para rodar os testes utilizando o Pytest, rode o comando:

```
uv run pytest
```
É recomendado rodar os testes sempre que alguma alteração for feita.

Para mais informações sobre o Pytest, acesse: [Pytest Docs](https://docs.pytest.org/en/stable/)

#### Ruff

Para rodar o ruff para checar possíveis erros, rode o comando:

```
uvx ruff check
```

Para rodar o ruff para checar possíveis erros de linting e corrigí-los rode o comando:

```
uvx ruff check --fix
```

Para mais informações sobre o Ruff, acesse: [Ruff Docs](https://docs.astral.sh/ruff/)
