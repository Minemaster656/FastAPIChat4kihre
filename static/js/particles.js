$(document).ready(function() {
    const canvas = $('#particleCanvas')[0];
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Получение значения CSS переменной
    const particleColor = getComputedStyle(document.documentElement).getPropertyValue('--particle-color').trim();
    const particleCount = 100;
    const minParticleSize = 2; // Минимальный размер частиц
    const maxParticleSize = 16; // Максимальный размер частиц
    const minSpeed = 0.3; // Минимальная скорость
    const maxSpeed = 1.5; // Максимальная скорость
    const particles = [];

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * (maxParticleSize - minParticleSize) + minParticleSize; // Случайный размер
            this.amplitude = Math.random() * 50 + 25;
            this.frequency = Math.random() * 0.02 + 0.01;
            this.speed = Math.random() * (maxSpeed - minSpeed) + minSpeed; // Случайная скорость
            this.offset = Math.random() * Math.PI * 2;
        }

        update() {
            this.x += this.speed;
            if (this.x > canvas.width) {
                this.x = 0;
            }
            this.y += Math.sin((this.x + this.offset) * this.frequency) * this.amplitude * 0.01;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = particleColor;
            ctx.fill();
        }
    }

    function initParticles() {
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });

        requestAnimationFrame(animateParticles);
    }

    initParticles();
    animateParticles();

    $(window).resize(function() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
});
