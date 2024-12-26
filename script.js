async function launchCodespace() {
    document.getElementById('status').innerText = 'Идет создание Codespace...';
    require('dotenv').config();

    const repoName = "dashMaket2review";
    const branch = "main";
    const token = process.env.TOKEN;
    
    try {
        const response = await fetch('https://api.github.com/sam5213/codespaces', {
            method: 'POST',
            headers: {
                Authorization: 'Bearer ${token}',
                Accept: 'application/vnd.github+json'
            },
            body: JSON.stringify({
                repository: {
                    id: process.env.REPO_ID,
                    default_branch: branch,
                    path: "/"
                },
                machine: "standardLinux32gb",
                devcontainer_path: ".devcontainer/devcontainer.json", // Путь к devcontainer.json
                location: "West Europe" // Регион расположения Codespace
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create Codespace');
        }

        const data = await response.json();
        console.log(data);

        // Ожидание завершения выполнения скрипта post_create.sh
        await waitForPublicUrl();

        // Получение публичного URL из файла public_url.txt
        const publicUrlResponse = await fetch("/public_url.txt");
        const publicUrl = await publicUrlResponse.text();

        // Перенаправление на публичный URL
        window.location.href = publicUrl;
    } catch (error) {
        alert("Ошибка при создании Codespace: " + error.message);
    }
}

// Функция ожидания завершения выполнения скрипта post_create.sh
async function waitForPublicUrl() {
    while (true) {
        try {
            const response = await fetch("/public_url.txt");
            if (response.status === 200) {
                return; // Файл существует, значит скрипт завершен
            }
        } catch (error) {}
        await new Promise(resolve => setTimeout(resolve, 1000)); // Ждем 1 секунду перед следующей попыткой
    }
}