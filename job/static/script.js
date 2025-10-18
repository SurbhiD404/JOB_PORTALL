function handleGoogleSignIn(response) {
    // Send ID token to Django backend
    fetch('http://localhost:8000/api/job/oauth/google/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token: response.credential })
    })
    .then(res => res.json())
    .then(data => {
        if (data.user) {
            // Show user info
            document.getElementById('user-info').style.display = 'block';
            document.getElementById('user-name').textContent = data.user.username;
            document.getElementById('user-email').textContent = data.user.email;
            document.getElementById('error-message').style.display = 'none';
        } else {
            // Show error
            document.getElementById('error-message').textContent = data.detail || 'Login failed.';
            document.getElementById('error-message').style.display = 'block';
        }
    })
    .catch(() => {
        document.getElementById('error-message').textContent = 'Error connecting to server.';
        document.getElementById('error-message').style.display = 'block';
    });
}