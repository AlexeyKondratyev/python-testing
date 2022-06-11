# python-testing

> Подключение к redis - `store.py`
## Запуск тестов

> все тесты
```
python -m unittest discover test
```
> fileds tests
```
python -m unittest test.test_fields
```
> api tests
- запустить redis
```
docker run --name redis -d redis
```
- запустить тесты
```
python -m unittest test.test_api
```
