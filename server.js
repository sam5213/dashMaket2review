const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/create-codespace', async (req, res) => {
    const { repoName, branch, repoId } = req.body;

    try {
        const response = await axios.post('https://api.github.com/sam5213/codespaces', {
            repository: {
                id: repoId,
                default_branch: branch,
                path: "/"
            },
            machine: "standardLinux32gb",
            devcontainer_path: ".devcontainer/devcontainer.json",
            location: "West Europe"
        }, {
            headers: {
                Authorization: `Bearer ${process.env.TOKEN}`,
                Accept: 'application/vnd.github+json'
            }
        });

        res.json({ success: true, url: response.data.html_url });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});