# FACIAL_RECOGNITION
## PARA RODAR O PROJETO
- É necessario ter instalado:
    - Python;
    - OpenCV;

- Instalar o OpenCV, pode dar bastante trabalho. Mas sigam os tutoriais na internet, eles vão dar certo.

- Além disso, é necessário adicionar uma pasta adicional no projeto, que atualmente está no .gitignore e devem permanecer lá devido ao teor do tamanho dela.

- Esta pasta são é a '/assets/', e ela contém:
    - database: *todas as imagens testes das pessoas*
    - suspects: *conterá as fotos do suspeito atual*;
    - faces: *conterá as fotos dos rostos dos suspeitos, já devidamente normalizadas.*
    - videos: *contém os vídeos utilizados para encontrar os rostos*

Esta pasta encontra-se no drive do projeto, encontrado no link:
 
E deve ser adicionada ao root do projeto.

Perceba que somente as pastas *suspects* e *videos* estão populadas com imagens/videos. Isso acontece pois o preenchimento da pasta *faces* ocorre durante o processo do algoritmo.

## SEQUÊNCIA DE COMO RODAR
1. Primeiro, deve-se copiar as fotos de **uma pessoa** da pasta *database* para pasta *suspects*;
2. Em seguida, deve-se rodar o arquivo *preparing.py*. Note que as fotos das pessoas na pasta database seguem o seguinte padrão: "Pessoa.X.YY". X representa o Id da pessoa e YY o número da foto da pessoa. Quando você rodar o arquivo *preparing.py*, será pedido que você entre o id do atual suspeito. Esse id é o "X" no nome das fotos da pessoa;
3. Em seguida delete as fotos da pasta *suspects*.
4. Repita os passos 1, 2 e 3 para todas as pessoas da pasta *database*;
5. Após finalizar de preencher a pasta suspects com as imagens tratadas dos rostos, rode o arquivo *training.py*; 
6. Por fim, é só rodar o arquivo *recognizing.py*. Para fechar a reproduão do video, basta apertar "Q";