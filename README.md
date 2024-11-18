# Bookler - PDF to Audiobook

**Bookler** é uma aplicação simples desenvolvida em Python para transformar arquivos PDF em audiolivros. A aplicação permite ao usuário escolher um arquivo PDF, visualizar uma prévia das páginas e ouvir a conversão do texto em áudio, com controles para ajustar a velocidade da fala.

## Funcionalidades

- **Escolha de Arquivo PDF**: O usuário pode selecionar um arquivo PDF para conversão.
- **Visualização de Página**: Visualiza uma imagem gerada da página atual do PDF, facilitando a navegação.
- **Controle de Navegação**: O usuário pode navegar pelas páginas do PDF utilizando botões de "Próxima" e "Anterior".
- **Conversão para Áudio**: O texto extraído do PDF é convertido em áudio.
- **Controle de Velocidade**: O usuário pode ajustar a velocidade da voz para a conversão.
- **Execução em Segundo Plano**: O processo de conversão é executado em uma thread separada, garantindo que a interface não congele durante a operação.

## Tecnologias Utilizadas

- **Tkinter**: Para a interface gráfica do usuário (GUI).
- **PyMuPDF (fitz)**: Para abrir e extrair texto de arquivos PDF.
- **pyttsx3**: Para converter texto em áudio.
- **Pillow**: Para manipulação e exibição de imagens do PDF.

## Como Usar

### Pré-requisitos

Antes de rodar o projeto, você precisa ter Python instalado em sua máquina. Para instalar as dependências, basta rodar o seguinte comando:

```bash
pip install -r requirements.txt
