function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    document.querySelector(`button[onclick="switchTab('${tabId}')"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }

  function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
      input.type = 'text';
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
      input.classList.add('password-visible');
    } else {
      input.type = 'password';
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
      input.classList.remove('password-visible');
      
      // Добавляем анимацию тряски
      input.classList.add('password-shake');
      setTimeout(() => {
        input.classList.remove('password-shake');
      }, 200);
    }
  }

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const login = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Login': login,
          'Password': password
        }
      });

      const data = await response.json();
      
      if (response.ok && data.JWT) {
        sessionStorage.setItem('JWT', data.JWT);
        window.location.href = '/chat';
      } else {
        alert(data.message);
        console.log(data.message, response);
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Произошла ошибка при входе');
    }
  });

  document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('register-name').value;
    const login = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name,
          login: login,
          password: password
        })
      });

      const data = await response.json();
      
      if (response.ok && data.JWT) {
        sessionStorage.setItem('JWT', data.JWT);
        window.location.href = '/chat';
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Произошла ошибка при регистрации');
    }
  });