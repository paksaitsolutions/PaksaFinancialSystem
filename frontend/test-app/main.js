console.log('Vite test app is running!');

// Simple DOM update
document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    const p = document.createElement('p');
    p.textContent = 'JavaScript is working!';
    p.style.color = 'blue';
    app.appendChild(p);
});
