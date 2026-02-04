const API_BASE = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const resetForm = document.getElementById('resetForm');
    const confirmResetForm = document.getElementById('confirmResetForm');
    const messageDiv = document.getElementById('message');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            try {
                const response = await fetch(`${API_BASE}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('token', data.access_token);
                    window.location.href = 'dashboard.html';
                } else {
                    window.location.href = 'login_error.html';
                }
            } catch (error) {
                messageDiv.textContent = 'Error logging in';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            try {
                const response = await fetch(`${API_BASE}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();
                if (response.ok) {
                    window.location.href = 'register_success.html';
                } else {
                    messageDiv.textContent = data.detail;
                }
            } catch (error) {
                messageDiv.textContent = 'Error registering';
            }
        });
    }

    if (resetForm) {
        resetForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            try {
                const response = await fetch(`${API_BASE}/reset-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });
                const data = await response.json();
                if (response.ok) {
                    messageDiv.textContent = `Reset token: ${data.reset_token} (In real app, this would be emailed)`;
                    document.getElementById('confirmEmail').value = email;
                    resetForm.style.display = 'none';
                    confirmResetForm.style.display = 'block';
                } else {
                    messageDiv.textContent = data.detail;
                }
            } catch (error) {
                messageDiv.textContent = 'Error sending reset request';
            }
        });
    }

    if (confirmResetForm) {
        confirmResetForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('confirmEmail').value;
            const resetToken = document.getElementById('resetToken').value;
            const newPassword = document.getElementById('newPassword').value;
            try {
                const response = await fetch(`${API_BASE}/reset-password/confirm`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, reset_token: resetToken, new_password: newPassword })
                });
                const data = await response.json();
                if (response.ok) {
                    messageDiv.textContent = 'Password reset successful! Please login.';
                    confirmResetForm.style.display = 'none';
                    resetForm.style.display = 'block';
                } else {
                    messageDiv.textContent = data.detail;
                }
            } catch (error) {
                messageDiv.textContent = 'Error resetting password';
            }
        });
    }

    // Check if on dashboard and token exists
    if (window.location.pathname.includes('dashboard.html')) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'index.html';
        } else {
            // Display dashboard content
            document.getElementById('userEmail').textContent = 'Logged in'; // In real app, decode token for email
        }
    }
});

// Logout function
function logout() {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}
