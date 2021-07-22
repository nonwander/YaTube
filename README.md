# YaTube - социальная сеть

Проект YaTube представляет собой блог-платформу с возможностью регистрации пользователей, управления публикациями пользователей, добавления групп к публикациям, подгрузки статики. Вы ставите чистую платформу, создаёте администратора и запускаете проект на локальном сервере - можно регистрироваться и создавать записи. <br /> Проект содержит юнит-тесты в отдельном пакете /tests приложения .posts.

___

## Установка.

### Cистемные требования:
    python==3.8.6
    Django==2.2.6

### Порядок установки.
1) Клонировать репозиторий
2) Установить зависимости из requirements.txt
3) Запустить проект

```python
git clone https://github.com/nonwander/hw05_final
pip install -r requirements.txt
python manage.py runserver
```
В завершении установки, перед тем, как развернуть проект, необходио создать профиль администратора сети Yatube:
```python
    python manage.py createsuperuser
```

### Особенности.
Проект запускается сервере разработчика Django на «внутреннем» IP-адресе 127.0.0.1 на порте 8000.
Проект хранит данные в предустановленной базе SQLite.

### Перспективные доработки проекта.
В перспективе подключить и настроить веб-сервер __nginx__ и wsgi-сервер __Gunicorn__.
Нужен отдельный сервер баз данных: в перспективе перейти на __PostgreSQL__. 

Ключевое приложение проекта - __.posts__
> модели (models.py):
>> User - стандартная модель get_user_model библиотеки django.contrib.auth;
>> <br /> Post - пост пользователя;
>> <br /> Group - группа объединения постов;
>> <br /> Comment - комментарий к посту пользователя;
>> <br /> Follow - подписчики (другие пользователи) к постам пользователя;

> админ-зона (admin.py):
>> управление объектами - можно публиковать новые записи или редактировать/удалять существующие;

> пакет с юнит-тестами /tests.

Все классы тестов наследуются от класса *TestCase* из пакета *django.test*.
Чтобы запустить юнит-тесты приложения __posts__, используйте команду:
```python
python3 manage.py test
```
