# Flask REST API

Запуск приложения (в БД есть пара записей для тестов):

```bash
$ virtualenv --python=python3 venv
$ cd venv
$ source bin/activate
$ git clone https://github.com/imflop/booklibrary
$ cd booklibrary
$ pip install -r requirements.txt
$ python myapp.py
```

Приложение будет доступно по адресу [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
SwaggerUI покажет все доступные эндпоинты

Заупск celery (в новой вкладке терминала) для задания со звездочкой

```bash
$ celery -A myapp.celery worker -B --concurrency=1
```

Testfixtures еще не поборол.