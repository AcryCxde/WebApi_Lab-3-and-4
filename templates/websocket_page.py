html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Уведомления</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            color: #333;
        }
        h1 {
            margin-bottom: 20px;
        }
        ul {
            list-style: none;
            padding: 0;
            width: 300px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            background-color: #fff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
        }
        li {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        li:last-child {
            border-bottom: none;
        }
        #messages {
            margin: 0;
        }
        footer {
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Уведомления WebSocket</h1>
    <ul id="messages">
        <li>Ожидание сообщений...</li>
    </ul>
    <footer>
        Подключение к серверу WebSocket...
    </footer>
    <script>
        const ws = new WebSocket("ws://127.0.0.1:8000/ws");

        ws.onmessage = function(event) {
            const messages = document.getElementById("messages");
            const message = document.createElement("li");
            message.textContent = event.data;
            messages.appendChild(message);
        };

        ws.onopen = function() {
            const footer = document.querySelector("footer");
            footer.textContent = "Соединение установлено.";
        };

        ws.onclose = function() {
            const footer = document.querySelector("footer");
            footer.textContent = "Соединение закрыто.";
        };

        ws.onerror = function() {
            const footer = document.querySelector("footer");
            footer.textContent = "Ошибка соединения.";
        };
    </script>
</body>
</html>
"""