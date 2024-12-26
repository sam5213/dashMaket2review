#!/bin/bash

# Выполняем команду из вашего файла YAML
echo "Выполнение команды..."
node server.js

# Получаем URL Codespace
codespace_url=$(codespace info --url)

# Генерируем публичный URL
public_url="http://example.com/?codespace_url=${codespace_url}"

# Сохраняем публичный URL в файл
echo $public_url > .devcontainer/public_url.txt