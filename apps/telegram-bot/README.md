# Aplicação em Python - Bot Telegram

Este projeto é uma aplicação em Python de um Bot no Telegram que interage com os usuários pegando algumas informações e enviando uma mensagem de resposta.

O código não foi desenvolvido por nós, ele foi somente adaptado a partir de um dos exemplos da biblioteca [python-telegram-bot](https://python-telegram-bot.readthedocs.io/en/stable/intro.html). O código fonte original pode ser obtido no repositório do GitHub [aqui](https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples).

Nós primeiramente apresentamos como seria o fluxo de desenvolvimento de uma aplicação Python, na máquina do desenvolvedor, utilizando virtualenv, um recurso bastante indicado para quem desenvolve em Python.

Depois apresentamos como seria o fluxo de desenvolvimento utilizando containers Docker para uma aplicação Python.

É importante destacar que esse fluxo será semelhante para qualquer tecnologia que seja utilizada para desenvolvimento de aplicações.

Você poderá clonar o repositório e a partir dele acompanhar as aulas.

Importante: Tanto para a execução com virtualenv quanto no Docker, você deverá criar um arquivo .env com as informações do token do bot no Telegram.

O conteúdo do arquivo .env, para este projeto de exemplo, é uma linha somente com o token do bot no Telegram.

````
TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ
````

O arquivo .env deverá ser salvo na mesma pasta do projeto.

Para saber mais em como gerar o token, procure o [BotFather](https://telegram.me/botfather).

Para saber mais sobre o arquivo .env, você pode olhar esse artigo [aqui](https://dev.to/jeffrey_barbosa/how-to-create-a-dotenv-file-for-your-python-application-1g6), este [outro](https://www.delftstack.com/pt/howto/python/dotenv-python/) ou ainda [esse](https://www.digitalocean.com/community/tutorials/how-to-use-dotenv-to-manage-environment-variables-in-python-3-and-django-apps).

