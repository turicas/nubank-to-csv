# `nubank-to-csv`

Script que converte o PDF da fatura do NuBank para CSV, já somando o IOF de
cada item (na fatura o IOF vem em itens separados).

O script converte o PDF para HTML (através do softwar e `pdftohtml`, contido no
pacote `poppler-utils`) e depois faz *parsing* do HTML, pegando somente os
dados desejados, e depois junta os itens de IOF com o item principal.

> Nota: como no PDF não existe a informação do ano, o script entende que o ano
> da fatura é o ano corrente.


## Instalação

### Dependências

Dependências do sistema:

    apt-get install poppler-utils

Dependências Python:

    pip install lxml rows

Caso prefira instalar tudo pelo sistema:

    apt-get install poppler-utils python-lxml python-rows


### Script

Baixe o arquivo `nubank.py` contido [nesse
repositório](https://github.com/turicas/nubank-to-csv).


## Uso

Primeiro converta o PDF para HTML e depois rode o script em cima do HTML.

Converter de PDF para HTML:

    pdftohtml XXX.pdf

onde `XXX.pdf` é o caminho para o arquivo de sua fatura. Isso irá gerar um
arquivo `XXXs.html` (dentre outros) no mesmo diretório.

Converter de HTML para CSV:

    python nubank.py XXXs.html minha-linda-fatura.csv

Agora é só brincar com o arquivo `minha-linda-fatura.csv`! ;-)
