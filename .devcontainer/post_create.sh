#!/bin/bash

# Выполняем команду из вашего файла YAML
echo "Выполнение команды..."
nohup python app.py &

# Получаем URL Codespace
codespace_url=$(codespace info --url)

# Генерируем публичный URL
public_url="https://sam5213.github.io/dashMaket2review/?codespace_url=${codespace_url}"

# Сохраняем публичный URL в файл
echo $public_url > .devcontainer/public_url.txt