class VFXEngine {
  constructor() {
    this.canvas = document.getElementById('vfx-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.mouse = { x: this.width / 2, y: this.height / 2, radius: 140 };

    this.mode = 'ambient_aurora';
    this.density = 'high';
    this.accentColor = '#00f0ff';
    this.secondaryColor = '#ff007f';

    this.particles = [];
    this.matrixColumns = [];
    this.gridOffset = 0;
    this.animFrameId = null;

    if (this.canvas) {
      this.initCanvas();
      this.bindEvents();
      this.setMode(this.mode);
      this.startLoop();
    }
  }

  initCanvas() {
    this.resize();
  }

  resize() {
    if (!this.canvas) return;
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.canvas.width = this.width;
    this.canvas.height = this.height;
    this.resetParticles();
  }

  bindEvents() {
    window.addEventListener('resize', () => this.resize());
    window.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });
  }

  setThemeColors(accent, secondary) {
    this.accentColor = accent;
    this.secondaryColor = secondary;
  }

  setMode(mode) {
    this.mode = mode;
    this.resetParticles();
  }

  setDensity(density) {
    this.density = density;
    this.resetParticles();
  }

  getParticleCount() {
    if (this.density === 'off') return 0;
    const base = (this.width * this.height) / 14000;
    switch (this.density) {
      case 'low': return Math.floor(base * 0.4);
      case 'medium': return Math.floor(base * 0.7);
      case 'high': return Math.floor(base * 1.1);
      case 'ultra': return Math.floor(base * 1.8);
      default: return Math.floor(base);
    }
  }

  resetParticles() {
    this.particles = [];
    const count = this.getParticleCount();

    if (this.mode === 'neural' || this.mode === 'stardust') {
      for (let i = 0; i < count; i++) {
        this.particles.push({
          x: Math.random() * this.width,
          y: Math.random() * this.height,
          vx: (Math.random() - 0.5) * 1.2,
          vy: (Math.random() - 0.5) * 1.2,
          radius: Math.random() * 2 + 1,
          baseRadius: Math.random() * 2 + 1,
          z: Math.random() * 1000 + 10
        });
      }
    } else if (this.mode === 'matrix_rain') {
      const fontSize = 16;
      const cols = Math.floor(this.width / fontSize);
      this.matrixColumns = [];
      for (let i = 0; i < cols; i++) {
        this.matrixColumns[i] = Math.random() * -50;
      }
    }
  }

  startLoop() {
    const loop = () => {
      this.render();
      this.animFrameId = requestAnimationFrame(loop);
    };
    loop();
  }

  render() {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.width, this.height);

    if (this.density === 'off') return;

    if (this.mode === 'ambient_aurora') {
      this.renderAmbientAurora();
    } else if (this.mode === 'neural') {
      this.renderNeuralConstellation();
    } else if (this.mode === 'matrix_rain') {
      this.renderMatrixRain();
    } else if (this.mode === 'stardust') {
      this.renderStardust();
    } else {
      this.renderAmbientAurora();
    }
  }

  renderAmbientAurora() {
    const ctx = this.ctx;
    ctx.save();

    if (!this.auroraTime) this.auroraTime = 0;
    this.auroraTime += 0.006;

    const mx = this.mouse ? this.mouse.x : this.width / 2;
    const my = this.mouse ? this.mouse.y : this.height / 3;

    const x1 = this.width * 0.28 + Math.sin(this.auroraTime * 0.7) * 70 + (mx - this.width / 2) * 0.04;
    const y1 = this.height * 0.22 + Math.cos(this.auroraTime * 0.9) * 50 + (my - this.height / 2) * 0.04;
    const r1 = Math.min(this.width, this.height) * 0.58;
    const g1 = ctx.createRadialGradient(x1, y1, 10, x1, y1, r1);
    g1.addColorStop(0, 'rgba(124, 58, 237, 0.16)');
    g1.addColorStop(0.5, 'rgba(139, 92, 246, 0.05)');
    g1.addColorStop(1, 'transparent');
    ctx.fillStyle = g1;
    ctx.fillRect(0, 0, this.width, this.height);

    const x2 = this.width * 0.74 + Math.cos(this.auroraTime * 0.8) * 80 - (mx - this.width / 2) * 0.03;
    const y2 = this.height * 0.3 + Math.sin(this.auroraTime * 0.6) * 60 - (my - this.height / 2) * 0.03;
    const r2 = Math.min(this.width, this.height) * 0.52;
    const g2 = ctx.createRadialGradient(x2, y2, 10, x2, y2, r2);
    g2.addColorStop(0, 'rgba(16, 185, 129, 0.13)');
    g2.addColorStop(0.45, 'rgba(6, 182, 212, 0.05)');
    g2.addColorStop(1, 'transparent');
    ctx.fillStyle = g2;
    ctx.fillRect(0, 0, this.width, this.height);

    const x3 = this.width * 0.5 + Math.sin(this.auroraTime * 0.5) * 50;
    const y3 = this.height * 0.68 + Math.cos(this.auroraTime * 0.7) * 40;
    const r3 = Math.min(this.width, this.height) * 0.62;
    const g3 = ctx.createRadialGradient(x3, y3, 10, x3, y3, r3);
    g3.addColorStop(0, 'rgba(79, 70, 229, 0.09)');
    g3.addColorStop(0.6, 'rgba(30, 27, 75, 0.03)');
    g3.addColorStop(1, 'transparent');
    ctx.fillStyle = g3;
    ctx.fillRect(0, 0, this.width, this.height);

    const count = Math.min(this.particles.length, 35);
    for (let i = 0; i < count; i++) {
      const p = this.particles[i];
      p.x += p.vx * 0.4;
      p.y += p.vy * 0.4;
      if (p.x < 0) p.x = this.width;
      if (p.x > this.width) p.x = 0;
      if (p.y < 0) p.y = this.height;
      if (p.y > this.height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius * 0.6, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
      ctx.fill();
    }

    ctx.restore();
  }

  renderNeuralConstellation() {
    const ctx = this.ctx;
    ctx.save();

    const maxDist = 120;
    const count = this.particles.length;

    for (let i = 0; i < count; i++) {
      const p = this.particles[i];

      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > this.width) p.vx *= -1;
      if (p.y < 0 || p.y > this.height) p.vy *= -1;

      const dx = this.mouse.x - p.x;
      const dy = this.mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < this.mouse.radius) {
        const force = (this.mouse.radius - dist) / this.mouse.radius;
        p.x -= (dx / dist) * force * 3;
        p.y -= (dy / dist) * force * 3;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = this.accentColor + 'cc';
      ctx.shadowBlur = 8;
      ctx.shadowColor = this.accentColor;
      ctx.fill();

      for (let j = i + 1; j < count; j++) {
        const p2 = this.particles[j];
        const dist2 = Math.hypot(p.x - p2.x, p.y - p2.y);
        if (dist2 < maxDist) {
          const alpha = 1 - dist2 / maxDist;
          ctx.strokeStyle = this.accentColor + Math.floor(alpha * 70).toString(16).padStart(2, '0');
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }
    }

    ctx.restore();
  }

  renderMatrixRain() {
    const ctx = this.ctx;
    ctx.save();
    ctx.font = '14px monospace';

    const glyphs = '01010101<>{}[]=+~ABCDEF';
    const fontSize = 16;

    for (let i = 0; i < this.matrixColumns.length; i++) {
      const char = glyphs[Math.floor(Math.random() * glyphs.length)];
      const x = i * fontSize;
      const y = this.matrixColumns[i] * fontSize;

      ctx.fillStyle = this.accentColor;
      ctx.shadowBlur = 8;
      ctx.shadowColor = this.accentColor;
      ctx.fillText(char, x, y);

      if (y > this.height && Math.random() > 0.975) {
        this.matrixColumns[i] = 0;
      }
      this.matrixColumns[i] += 0.8;
    }

    ctx.restore();
  }

  renderStardust() {
    const ctx = this.ctx;
    const centerX = this.width / 2;
    const centerY = this.height / 2;

    ctx.save();
    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      p.z -= 4.5;
      if (p.z <= 0) {
        p.z = 1000;
        p.x = Math.random() * this.width;
        p.y = Math.random() * this.height;
      }

      const k = 250 / p.z;
      const px = (p.x - centerX) * k + centerX;
      const py = (p.y - centerY) * k + centerY;

      if (px >= 0 && px <= this.width && py >= 0 && py <= this.height) {
        const size = (1 - p.z / 1000) * 3;
        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fillStyle = this.accentColor;
        ctx.shadowBlur = 6;
        ctx.shadowColor = this.accentColor;
        ctx.fill();
      }
    }
    ctx.restore();
  }
}

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.enabled = false;
    this.volume = 0;
  }

  initAudioContext() {}
  playClick() {}
  playScan() {}
  playAlert() {}
  playHumanize() {}
  playSuccess() {}
  playRadarPing() {}
}

window.vfx = new VFXEngine();
window.sound = new SoundEngine();
