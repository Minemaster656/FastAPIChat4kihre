let jwt = sessionStorage.getItem("JWT");
let current_uuid = null;
let fetchedJWT = false;
let messages = {}; // {chat_uuid: [messages]}
let current_chat_uuid = null;
let websocket = null;
let chats = [];
// Проверяем наличие JWT при загрузке страницы
window.onload = async function () {
  ///const jwt = sessionStorage.getItem('JWT');

  if (!jwt) {
    // Если токена нет - редирект на авторизацию

    fetchedJWT = true;
    window.location.href = "/auth";
    return;
  } else {
    setTimeout(() => {
      setInterval(refreshToken, 10 * 60 * 1000);
    }, 1000 * 600);
  }

  try {
    // Пробуем обновить токен
    const response = await fetch("/auth/refresh", {
      method: "POST",
      headers: {
        Authorization: jwt,
      },
    });

    if (response.status === 401 || response.status === 400) {
      // Если токен невалидный - редирект на авторизацию
      alert("Сессия истекла. Необходима повторная авторизация.");
      window.location.href = "/auth";
      return;
    }

    if (response.ok) {
      // Обновляем токен в sessionStorage
      const data = await response.json();
      if (!data.JWT) {
        alert("Ошибка при обновлении токена");
        window.location.href = "/auth";
        return;
      }
      sessionStorage.setItem("JWT", data.JWT);
      jwt = data.JWT;
      fetchedJWT = true;
      current_uuid = data.UUID;
      connectToChat();
      setTimeout(() => {
        setInterval(refreshToken, 10 * 60 * 1000);
      }, 1000 * 600);
    }
  } catch (error) {
    alert("Ошибка при обновлении токена:", error);

    window.location.href = "/auth";
  }
};
// Функция для обновления JWT
async function refreshToken() {
  try {
    const response = await fetch("/auth/refresh", {
      method: "POST",
      headers: {
        Authorization: jwt,
      },
    });

    if (response.status === 401) {
      alert("Сессия истекла. Необходима повторная авторизация.");
      window.location.href = "/auth";
      return;
    }

    if (response.ok) {
      const data = await response.json();
      if (!data.JWT) {
        alert("Ошибка при обновлении токена");
        window.location.href = "/auth";
        return;
      }
      sessionStorage.setItem("JWT", data.JWT);
      jwt = data.JWT;
    }
  } catch (error) {
    alert("Ошибка при обновлении токена:", error);
    // При таймауте или другой ошибке оставляем пользователя на странице
  }
}
async function connectToChat() {
  console.log("Connecting to chat");
  websocket = new WebSocket(websocketAddress);
  websocket.onmessage = function (event) {
    const message = JSON.parse(event.data);
    makeMessage(message);
  };
  websocket.onopen = async function () {
    console.log("Connected to chat");
    const jwt = sessionStorage.getItem("JWT");
    refreshChats();
  };
  websocket.onclose = async function () {
    console.log("Disconnected from chat");
    websocket = null;
    connectToChat();
  };
  websocket.onerror = function (error) {
    console.error("WebSocket error:", error);
    websocket = null;
  };
}

// Запускаем обновление токена каждые 10 минут
function makeMessage(message) {}

async function refreshChats() {
  const response = await fetch("/clientapi/fetchchats", {
    method: "GET",
    headers: {
      Authorization: jwt,
    },
  });

  if (response.ok) {
    const chats_response = await response.json();
    console.log("Fetched chats:", chats_response);
    console.log(chats_response.result);
    // Здесь можно добавить код для обработки полученных чатов
    chats = chats_response.result;
    buildChats();
  } else {
    // console.error("Ошибка при получении чатов:", response.statusText);
    refreshToken().then(() => {
      setTimeout(() => {
        refreshChats();
      }, 1000);
    });
  }
}

async function buildChats() {
  console.log("Building chats");
  const chats_container = document.getElementById("chats-list");
  chats_container.innerHTML = "";
  console.log(chats);
  chats.forEach((chat) => {
    const chat_element = document.createElement("div");
    chat_element.classList.add("chat-item");
    chat_element.textContent = chat.name;
    chat_element.addEventListener("click", () => {
      current_chat_uuid = chat.UUID;
      const selectedChat = document.querySelector(".selected-chat");
        if (selectedChat) {
          selectedChat.classList.remove("selected-chat");
      }
      chat_element.classList.add("selected-chat");
      refreshMessages().then(() => {
        loadHistory();
      });
    });
    chats_container.appendChild(chat_element);
  });
}
async function refreshMessages() {
  if (!current_chat_uuid) {
    return;
  }
  const response = await fetch("/clientapi/fetchmessages/latest", {
    method: "GET",
    headers: {
      Authorization: jwt,
      chat_uuid: current_chat_uuid,
    },
  });

  if (response.ok) {
    const messages_response = await response.json();
    messages[current_chat_uuid] = messages_response.result; // Сохраняем сообщения по uuid чата
  }
}
async function loadHistory() {
  const messages_container = document.querySelector(".chat-messages");
  messages_container.innerHTML = ""; // Очищаем контейнер перед загрузкой новых сообщений

  if (messages[current_chat_uuid]) {
    messages[current_chat_uuid].forEach((message) => {
      const message_element = document.createElement("div");
      message_element.classList.add("message-item");
      message_element.textContent = message.content; // Предполагается, что у сообщения есть поле content
      messages_container.appendChild(message_element);
    });
  } else {
    console.log("Нет сообщений для этого чата.");
  }
}
async function sendMessage(content) {
  if (!current_chat_uuid) {
    console.error("Нет выбранного чата для отправки сообщения.");
    return;
  }

  const message = {
    type: "SEND_MESSAGE",
    jwt: jwt,
    chat_uuid: current_chat_uuid,
    content: content,
  };

  // Отправка сообщения через вебсокет
  websocket.send(JSON.stringify(message));
}

