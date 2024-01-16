![example workflow](https://github.com/babichdenis/foodgram-project-react/actions/workflows/main.yml/badge.svg) 




# О проекте
«Фудграм» — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
У веб-приложения уже есть готовый фронтенд — это одностраничное SPA-приложение, написанное на фреймворке React. 


## Стек технологий

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?&style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker%20-%230db7ed.svg?&style=for-the-badge&logo=docker&logoColor=white)
![GitHub](https://img.shields.io/badge/github%20-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions%20-%232671E5.svg?&style=for-the-badge&logo=github%20actions&logoColor=white)

### Необходимые инструменты

* [Python](https://www.python.org/)
* [Pip](https://pypi.org/project/pip/)
* [Django](https://www.djangoproject.com/)
* [Docker](https://www.docker.com/)


## Настройка и Развертывание
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/babichdenis/foodgram-project-react.git
```

```
cd foodgram
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```


### Настройка Переменных Окружения
Создайте файл `.env` в корневой директории и заполните необходимые переменные:

- DB_ENGINE=django.db.backends.postgresql
- DB_NAME=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- DB_HOST=db
- DB_PORT=5432
- SECRET_KEY=
- ALLOWED_HOSTS=
- DEBUG=True

### Запуск с Docker

docker-compose up -d

## Как задеплоить проект на сервер

- Подключаемся к удаленному серверу. У вас должен быть установлен Nginx. Устанавливаем Docker Compose:

```bash
sudo apt update

sudo apt install curl

curl -fSL https://get.docker.com -o get-docker.sh

sudo sh ./get-docker.sh

sudo apt install docker-compose-plugin 
```

- Создаем на сервере директорию и переходим в нее:

```bash
mkdir foodgram

cd foodgram
```

В директорию foodgram/infra копируем файлы docker-compose.yml, nginx.conf и .env.
```
- Запускаем docker compose:
```

- sudo docker compose -f docker-compose.yml pull
- sudo docker compose -f docker-compose.yml down
- sudo docker compose -f docker-compose.yml up -d
```
- Выполните миграции:
```
- sudo docker compose -f docker-compose.yml pull
- sudo docker compose -f docker-compose.yml down
- sudo docker compose -f docker-compose.yml up -d
- sudo docker compose exec backend python manage.py makemigrations users
- sudo docker compose exec backend python manage.py makemigrations recipes
- sudo docker compose -f docker-compose.yml exec backend python manage.py migrate users
- sudo docker compose -f docker-compose.yml exec backend python manage.py migrate recipes
- sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input
- sudo docker compose exec backend python manage.py importcsv
```

- Команда для сбора статики:
```
docker-compose.yml exec backend python manage.py collectstatic --no-input
```

Команда для создания суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```

- Команда для подгрузки ингредиентов:
```
docker compose exec backend python manage.py importcsv
```
- В редакторе nano открываем конфигурацию Nginx, а затем добавляем следующие настройки:


```
sudo nano /etc/nginx/sites-enabled/default

location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:7000;
}
```

- Проверяем работоспособность и перезапускаем Nginx:

```
sudo nginx -t

sudo service nginx reload
```

## Как настроить CI/CD

Добавляем секреты в GitHub Actions:
- DOCKER_USERNAME - никнейм в DockerHub
- DOCKER_PASSWORD - пароль в DockerHub
- HOST - ip-адрес сервера
- USER - имя пользователя
- SSH_KEY - закрытый ssh-ключ сервера
- SSH_PASSPHRASE - пароль для ssh-ключа
- TELEGRAM_TO - id аккаунта в Телеграме
- TELEGRAM_TOKEN - токен вашего бота
- SECRET_KEY - секретный ключ проекта
- DEBUG - режим отладки
- ALLOWED_HOSTS - список разрешённых хостов для запуска проекта


Workflow вызывается при пуше в репозиторий

По завершению деплоя вы будете уведомлены в телеграме!

### Файрвол и SSL-сертификат (Let's Encrypt)
- Настройте файрвол на порты 80, 443 и 22, а затем включите и проверьте:
```shell
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH

sudo ufw enable
sudo ufw status
```
- Установите certbot
```shell
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot 
```
- Запустите certbot и укажите номер домена для активации HTTPS:
```shell
sudo certbot --nginx
```

## Автор:
**[Denis Babich](https://github.com/babichdenis/)**


