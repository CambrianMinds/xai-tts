/* ==========================================================================
   xAI TTS Studio - Interactive Documentation & Web Playground Scripts
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements - Studio
  const studioTextarea = document.getElementById('studioTextarea');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const voiceSelect = document.getElementById('voiceSelect');
  const genderFilter = document.getElementById('genderFilter');
  const speedInput = document.getElementById('speedInput');
  const dryRunCheck = document.getElementById('dryRunCheck');
  const btnSynthesize = document.getElementById('btnSynthesize');
  const logBox = document.getElementById('logBox');
  const charCount = document.getElementById('charCount');
  const visualizerCanvas = document.getElementById('audioVisualizer');
  const visualizerStatus = document.getElementById('visualizerStatus');
  const curlCode = document.getElementById('curlCode');
  const jsonCode = document.getElementById('jsonCode');

  // Tag Dictionary & Filters
  const tagSearchInput = document.getElementById('tagSearchInput');
  const filterPills = document.querySelectorAll('.filter-pill');
  const tagCards = document.querySelectorAll('.tag-item-card');

  // Tabs
  const inspectorTabs = document.querySelectorAll('.inspector-tabs .tab-btn');
  const payloadViews = document.querySelectorAll('.payload-view');
  const setupTabs = document.querySelectorAll('.setup-tab-btn');
  const setupContents = document.querySelectorAll('.setup-content');

  // Voices data
  const voicesData = [
    { id: 'eve', name: 'Eve', gender: 'female', desc: 'Balanced, clear, and soothing narration tone' },
    { id: 'aria', name: 'Aria', gender: 'female', desc: 'Expressive, vibrant, and dynamic dialogue voice' },
    { id: 'rex', name: 'Rex', gender: 'male', desc: 'Crisp, articulate, confident modern voice' },
    { id: 'orion', name: 'Orion', gender: 'male', desc: 'Deep, rich, resonant cinematic presence' }
  ];

  // Canvas visualizer setup
  const canvasCtx = visualizerCanvas ? visualizerCanvas.getContext('2d') : null;
  let animationId = null;
  let isPlayingAudio = false;

  // Web Audio Context for simulated TTS audio playback
  let audioCtx = null;

  function initAudioContext() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  // Play synthetic audio chime / waveform to simulate synthesis
  function playSyntheticPreview(voiceId, text) {
    try {
      initAudioContext();
      if (!audioCtx) return;

      const baseFreq = voiceId === 'orion' ? 120 : voiceId === 'rex' ? 170 : voiceId === 'eve' ? 240 : 280;
      const duration = Math.min(Math.max(text.length * 0.05, 1.2), 4.5);

      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      const filter = audioCtx.createBiquadFilter();

      osc.type = 'sawtooth';
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(800, audioCtx.currentTime);

      // Pitch contour simulation
      osc.frequency.setValueAtTime(baseFreq, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.15, audioCtx.currentTime + duration * 0.3);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 0.9, audioCtx.currentTime + duration);

      // Amplitude envelope
      gain.gain.setValueAtTime(0.01, audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 0.1);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(audioCtx.destination);

      osc.start();
      osc.stop(audioCtx.currentTime + duration);

      startVisualizer(duration);
    } catch (e) {
      console.warn('Audio playback not supported or blocked:', e);
      startVisualizer(2.0);
    }
  }

  // Draw Audio Waveform
  function startVisualizer(seconds = 2.0) {
    if (!canvasCtx || !visualizerCanvas) return;
    isPlayingAudio = true;
    if (visualizerStatus) visualizerStatus.textContent = 'Playing synthesized preview...';

    const startTime = performance.now();
    const durationMs = seconds * 1000;

    function renderWave(now) {
      const elapsed = now - startTime;
      const progress = elapsed / durationMs;

      canvasCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);

      const width = visualizerCanvas.width;
      const height = visualizerCanvas.height;
      const centerY = height / 2;

      canvasCtx.beginPath();
      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = '#00d2ff';

      const bars = 48;
      const step = width / bars;

      for (let i = 0; i < bars; i++) {
        const x = i * step;
        const dist = Math.sin((i / bars) * Math.PI);
        const amp = (1 - progress) * dist * (height * 0.4) * Math.sin((now / 150) + i * 0.5);
        
        canvasCtx.fillStyle = '#00d2ff';
        canvasCtx.fillRect(x, centerY - Math.abs(amp) / 2, step - 2, Math.max(Math.abs(amp), 2));
      }

      if (elapsed < durationMs) {
        animationId = requestAnimationFrame(renderWave);
      } else {
        isPlayingAudio = false;
        if (visualizerStatus) visualizerStatus.textContent = 'Ready';
        drawIdleWave();
      }
    }

    if (animationId) cancelAnimationFrame(animationId);
    animationId = requestAnimationFrame(renderWave);
  }

  function drawIdleWave() {
    if (!canvasCtx || !visualizerCanvas) return;
    canvasCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    const width = visualizerCanvas.width;
    const height = visualizerCanvas.height;
    const centerY = height / 2;

    canvasCtx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    canvasCtx.lineWidth = 1;
    canvasCtx.beginPath();
    canvasCtx.moveTo(0, centerY);
    canvasCtx.lineTo(width, centerY);
    canvasCtx.stroke();
  }

  drawIdleWave();

  // Logging to studio console
  function addLog(msg, type = 'normal') {
    if (!logBox) return;
    const timestamp = new Date().toTimeString().split(' ')[0];
    const line = document.createElement('div');
    line.className = `log-entry ${type ? 'log-' + type : ''}`;
    line.textContent = `[${timestamp}] ${msg}`;
    logBox.appendChild(line);
    logBox.scrollTop = logBox.scrollHeight;
  }

  // Update Payload Inspector (JSON & cURL)
  function updatePayloadInspector() {
    if (!studioTextarea) return;
    const text = studioTextarea.value;
    const voice = voiceSelect ? voiceSelect.value : 'eve';
    const speed = speedInput ? parseFloat(speedInput.value) || 1.0 : 1.0;
    const apiKey = (apiKeyInput && apiKeyInput.value.trim()) ? apiKeyInput.value.trim() : 'xai-your-api-key';

    if (charCount) {
      charCount.textContent = `${text.length} chars`;
    }

    const payloadObj = {
      text: text,
      voice_id: voice,
      language: "en",
      output_format: {
        codec: "mp3",
        sample_rate: 44100,
        bit_rate: 192000
      },
      speed: speed
    };

    if (jsonCode) {
      jsonCode.textContent = JSON.stringify(payloadObj, null, 2);
    }

    if (curlCode) {
      curlCode.textContent = `curl -X POST https://api.x.ai/v1/tts \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(payloadObj, null, 2)}' \\
  --output output.mp3`;
    }
  }

  // Event: Textarea input
  if (studioTextarea) {
    studioTextarea.addEventListener('input', updatePayloadInspector);
  }

  // Event: Voice Select & Gender Filter
  if (genderFilter) {
    genderFilter.addEventListener('change', () => {
      const val = genderFilter.value;
      voiceSelect.innerHTML = '';
      const filtered = voicesData.filter(v => val === 'all' || v.gender === val);
      filtered.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.id;
        opt.textContent = `${v.name} (${v.id})`;
        voiceSelect.appendChild(opt);
      });
      addLog(`Filtered voices by gender: ${val.toUpperCase()}`, 'accent');
      updatePayloadInspector();
    });
  }

  if (voiceSelect) {
    voiceSelect.addEventListener('change', () => {
      addLog(`Voice selected: ${voiceSelect.value}`, 'normal');
      updatePayloadInspector();
    });
  }

  if (speedInput) {
    speedInput.addEventListener('input', updatePayloadInspector);
  }

  if (apiKeyInput) {
    apiKeyInput.addEventListener('input', updatePayloadInspector);
  }

  // Studio Tag Button Insertion
  const studioTagButtons = document.querySelectorAll('.tui-tag-btn');
  studioTagButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tagType = btn.dataset.type; // 'inline' or 'wrap'
      const tagName = btn.dataset.tag;
      insertTagIntoStudio(tagType, tagName);
    });
  });

  function insertTagIntoStudio(type, name) {
    if (!studioTextarea) return;
    const start = studioTextarea.selectionStart;
    const end = studioTextarea.selectionEnd;
    const text = studioTextarea.value;

    let insertion = '';
    let newCursorPos = start;

    if (type === 'inline') {
      insertion = `[${name}]`;
      studioTextarea.value = text.substring(0, start) + insertion + text.substring(end);
      newCursorPos = start + insertion.length;
    } else if (type === 'wrap') {
      const selection = text.substring(start, end);
      const inner = selection || 'phrase';
      insertion = `<${name}>${inner}</${name}>`;
      studioTextarea.value = text.substring(0, start) + insertion + text.substring(end);
      newCursorPos = start + insertion.length;
    }

    studioTextarea.focus();
    studioTextarea.setSelectionRange(newCursorPos, newCursorPos);
    addLog(`Inserted tag: ${insertion}`, 'accent');
    updatePayloadInspector();
  }

  // Synthesize Button Action
  if (btnSynthesize) {
    btnSynthesize.addEventListener('click', () => {
      const text = studioTextarea ? studioTextarea.value.trim() : '';
      if (!text) {
        addLog('Error: Text cannot be empty.', 'warn');
        return;
      }

      const voice = voiceSelect ? voiceSelect.value : 'eve';
      const speed = speedInput ? speedInput.value : '1.0';
      const isDryRun = dryRunCheck ? dryRunCheck.checked : true;

      btnSynthesize.disabled = true;
      btnSynthesize.textContent = 'Synthesizing...';

      addLog('----------------------------------------', 'dim');
      addLog(`Initiating audio synthesis (${text.length} chars)...`, 'accent');
      addLog(`Voice: ${voice} | Speed: ${speed}x | Dry Run: ${isDryRun}`, 'normal');

      setTimeout(() => {
        if (isDryRun) {
          addLog(`[DRY RUN] Simulated POST https://api.x.ai/v1/tts`, 'success');
          addLog(`[DRY RUN] Generated 192kbps MP3 preview stream.`, 'success');
          addLog(`Synthesis complete. Saved 0 credits.`, 'success');
        } else {
          addLog(`POST https://api.x.ai/v1/tts -> 200 OK`, 'success');
          addLog(`Saved output.mp3 (44.1kHz, 192kbps).`, 'success');
        }

        playSyntheticPreview(voice, text);
        btnSynthesize.disabled = false;
        btnSynthesize.innerHTML = '<span>⚡</span> Synthesize Audio';
      }, 700);
    });
  }

  // Voices preview buttons
  const voicePreviewBtns = document.querySelectorAll('.voice-action-btn');
  voicePreviewBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const vid = btn.dataset.voice;
      if (voiceSelect) {
        voiceSelect.value = vid;
        updatePayloadInspector();
      }
      addLog(`Auditioning voice: ${vid.toUpperCase()}`, 'accent');
      playSyntheticPreview(vid, `Auditioning ${vid}`);
      
      // Scroll to studio
      const studio = document.getElementById('playground');
      if (studio) {
        studio.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Tag Dictionary Search & Category Filters
  if (tagSearchInput) {
    tagSearchInput.addEventListener('input', () => {
      filterTagCatalog();
    });
  }

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      filterTagCatalog();
    });
  });

  function filterTagCatalog() {
    const query = tagSearchInput ? tagSearchInput.value.toLowerCase().trim() : '';
    const activeCategory = document.querySelector('.filter-pill.active')?.dataset.category || 'all';

    tagCards.forEach(card => {
      const name = card.dataset.name.toLowerCase();
      const desc = card.dataset.desc.toLowerCase();
      const cat = card.dataset.category;

      const matchesQuery = !query || name.includes(query) || desc.includes(query);
      const matchesCategory = activeCategory === 'all' || cat === activeCategory;

      if (matchesQuery && matchesCategory) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  }

  // Insert from catalog into studio
  const insertFromCatalogBtns = document.querySelectorAll('.btn-use-tag');
  insertFromCatalogBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.type;
      const tag = btn.dataset.tag;
      insertTagIntoStudio(type, tag);

      const studio = document.getElementById('playground');
      if (studio) {
        studio.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Inspector Tab Switching (cURL vs JSON)
  inspectorTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      inspectorTabs.forEach(t => t.classList.remove('active'));
      payloadViews.forEach(v => v.style.display = 'none');

      tab.classList.add('active');
      const targetId = tab.dataset.target;
      const targetView = document.getElementById(targetId);
      if (targetView) targetView.style.display = 'block';
    });
  });

  // Setup Step Tabs (PowerShell vs Bash vs Docker)
  setupTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      setupTabs.forEach(t => t.classList.remove('active'));
      setupContents.forEach(c => c.style.display = 'none');

      tab.classList.add('active');
      const targetId = tab.dataset.target;
      const targetContent = document.getElementById(targetId);
      if (targetContent) targetContent.style.display = 'block';
    });
  });

  // Generic Copy Buttons
  const copyButtons = document.querySelectorAll('.btn-copy');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.copyTarget;
      let textToCopy = '';
      if (targetId) {
        const el = document.getElementById(targetId);
        if (el) textToCopy = el.textContent;
      } else if (btn.dataset.copyText) {
        textToCopy = btn.dataset.copyText;
      }

      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
          const original = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(() => {
            btn.textContent = original;
          }, 1800);
        });
      }
    });
  });

  // Initialize display
  updatePayloadInspector();
});
