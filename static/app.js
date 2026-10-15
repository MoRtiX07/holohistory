/**
 * Holo Persona — Frontend Application Script (v2.6)
 * Quick Responsive Engine, Live Talking Animation, Clean SVGs, and Essential Suite
 */

// State
let personas = [];
let currentPersonaId = "einstein";
let isKioskMode = false;
let isMasterAuthenticated = false;

let chatHistories = {
  einstein: [],
  kalam: [],
  tesla: []
};
let latestContextChunks = [];
let ttsEnabled = true;
let sfxEnabled = true;
let currentSpeedMultiplier = 1.0;
let isSpeaking = false;
let isRecording = false;
let recognition = null;
let activeCategory = "All";

// Web Audio API Sound Synthesizer (Fast & Clean)
let audioCtx = null;
function getAudioContext() {
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) audioCtx = new AudioContext();
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playSound(type) {
  if (!sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === 'click') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(900, now);
      osc.frequency.exponentialRampToValueAtTime(450, now + 0.03);
      gain.gain.setValueAtTime(0.06, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.03);
      osc.start(now);
      osc.stop(now + 0.03);
    } else if (type === 'transmit') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(560, now);
      osc.frequency.exponentialRampToValueAtTime(1120, now + 0.06);
      gain.gain.setValueAtTime(0.09, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.06);
      osc.start(now);
      osc.stop(now + 0.06);
    } else if (type === 'receive') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(700, now);
      osc.frequency.setValueAtTime(950, now + 0.05);
      osc.frequency.setValueAtTime(1400, now + 0.1);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.18);
      osc.start(now);
      osc.stop(now + 0.18);
    } else if (type === 'switch') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(360, now);
      osc.frequency.exponentialRampToValueAtTime(720, now + 0.1);
      gain.gain.setValueAtTime(0.1, now);
      gain.gain.linearRampToValueAtTime(0.001, now + 0.14);
      osc.start(now);
      osc.stop(now + 0.14);
    }
  } catch (err) {
    // Ignore audio restrictions
  }
}

// Initial greetings per persona
const INITIAL_GREETINGS = {
  einstein: "Greetings, my dear friend. I am Albert Einstein. The universe around us is deeply harmonious and orderly, revealing its truths only to persistent curiosity and humble wonder. What questions of nature, space, time, or human fellowship shall we explore today?",
  kalam: "Warm greetings and welcome, my young friend. I am Dr. A.P.J. Abdul Kalam. What a pleasure it is to connect with you. Tell me, what are your dreams, your ideas, and what challenges can we conquer together so that you may fly high like an arrow into the future?",
  tesla: "Salutations. I am Nikola Tesla. You are conversing directly with the current of invention and mind. My entire life was dedicated to unlocking the unseen energies of nature for the upliftment of mankind. Inquire freely of alternating current, wireless resonance, or the future of our electrical world."
};

// Clean SVG Icons for Buttons
const SVG_ICONS = {
  play: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`,
  copy: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
  context: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`
};

// DOM Elements
const personaNav = document.getElementById("persona-nav");
const kioskBanner = document.getElementById("kiosk-banner");
const kioskTitle = document.getElementById("kiosk-title");
const modeBadge = document.getElementById("mode-badge");
const holoEra = document.getElementById("holo-era");
const holoStatus = document.getElementById("holo-status");
const avatarPhoto = document.getElementById("avatar-photo");
const personaAvatarWrapper = document.getElementById("persona-avatar-wrapper");
const grandPortraitContainer = document.getElementById("grand-portrait-container");
const holoHudCode = document.getElementById("holo-hud-code");
const stopSpeakingBtn = document.getElementById("stop-speaking-btn");
const audioRing = document.getElementById("audio-ring");
const dossierName = document.getElementById("dossier-name");
const dossierTitle = document.getElementById("dossier-title");
const dossierQuote = document.getElementById("dossier-quote");
const dossierWords = document.getElementById("dossier-words");
const milestonesTrack = document.getElementById("milestones-track");
const channelName = document.getElementById("channel-name");
const categoryFilterBar = document.getElementById("category-filter-bar");
const messagesContainer = document.getElementById("messages-container");
const promptsContainer = document.getElementById("prompts-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const recStatus = document.getElementById("rec-status");
const waveform = document.getElementById("waveform-container");
const clearChatBtn = document.getElementById("clear-chat-btn");
const ttsToggleBtn = document.getElementById("tts-toggle-btn");
const ttsLabel = document.getElementById("tts-label");
const sfxToggleBtn = document.getElementById("sfx-toggle-btn");
const memoryToggleBtn = document.getElementById("memory-toggle-btn");
const chunkCountBadge = document.getElementById("chunk-count-badge");
const contextDrawer = document.getElementById("context-drawer");
const drawerBackdrop = document.getElementById("drawer-backdrop");
const closeDrawerBtn = document.getElementById("close-drawer-btn");
const drawerContent = document.getElementById("drawer-content");
const exportChatBtn = document.getElementById("export-chat-btn");
const fullscreenBtn = document.getElementById("fullscreen-btn");
const toastMsg = document.getElementById("toast-msg");

// Modals: Access Gate & QR Studio
const accessGateModal = document.getElementById("access-gate-modal");
const operatorPinInput = document.getElementById("operator-pin-input");
const verifyPinBtn = document.getElementById("verify-pin-btn");
const pinErrorMsg = document.getElementById("pin-error-msg");
const qrStudioBtn = document.getElementById("qr-studio-btn");
const qrStudioModal = document.getElementById("qr-studio-modal");
const closeQrModalBtn = document.getElementById("close-qr-modal-btn");
const qrCardsContainer = document.getElementById("qr-cards-container");

// Floating Artifacts, Surprise Me Warp & Codex Modal Elements
const floatingArtifactsLayer = document.getElementById("floating-artifacts-layer");
const warpFlare = document.getElementById("warp-flare");
const surpriseBtn = document.getElementById("surprise-btn");
const artifactsCodexBtn = document.getElementById("artifacts-codex-btn");
const artifactsCodexModal = document.getElementById("artifacts-codex-modal");
const closeCodexModalBtn = document.getElementById("close-codex-modal-btn");
const codexGridContainer = document.getElementById("codex-grid-container");
const codexModalTitle = document.getElementById("codex-modal-title");
const codexModalSubtitle = document.getElementById("codex-modal-subtitle");

// Initialize Application
async function init() {
  setupEventListeners();
  setupSpeechRecognition();
  await loadPersonas();

  // Check URL parameters for QR Kiosk Mode
  const urlParams = new URLSearchParams(window.location.search);
  const targetPersona = urlParams.get("persona");
  const kioskParam = urlParams.get("kiosk") === "true";
  const masterParam = urlParams.get("master") === "true";

  if ((targetPersona || kioskParam) && !masterParam) {
    isKioskMode = true;
    const personaToLock = (targetPersona && ["einstein", "kalam", "tesla"].includes(targetPersona.toLowerCase()))
      ? targetPersona.toLowerCase()
      : "einstein";
    enterKioskMode(personaToLock);
  } else {
    const hasAuth = sessionStorage.getItem("master_auth") === "true" || urlParams.get("master") === "true";
    if (hasAuth) {
      isMasterAuthenticated = true;
      const initialPersona = (targetPersona && ["einstein", "kalam", "tesla"].includes(targetPersona.toLowerCase()))
        ? targetPersona.toLowerCase()
        : "einstein";
      selectPersona(initialPersona);
    } else {
      accessGateModal.classList.remove("hidden");
    }
  }
}

// Enter Single-Persona Locked Kiosk Mode
function enterKioskMode(personaId) {
  isKioskMode = true;
  accessGateModal.classList.add("hidden");
  personaNav.classList.add("hidden");
  kioskBanner.classList.remove("hidden");
  qrStudioBtn.classList.add("hidden");
  modeBadge.textContent = "QR EXHIBIT STATION";
  selectPersona(personaId);
}

window.launchSingleKiosk = function(personaId) {
  window.location.href = `/?persona=${personaId}&kiosk=true`;
};

// Fetch Personas from API
async function loadPersonas() {
  try {
    const res = await fetch("/api/personas");
    if (!res.ok) throw new Error("Failed to load personas");
    personas = await res.json();
    renderPersonaNav();
  } catch (err) {
    console.error("Error loading personas:", err);
  }
}

// Render Header Persona Tabs
function renderPersonaNav() {
  personaNav.innerHTML = "";
  personas.forEach(p => {
    const btn = document.createElement("button");
    btn.className = `persona-tab-btn ${p.id === currentPersonaId ? "active" : ""}`;
    btn.setAttribute("data-id", p.id);
    const shortName = p.name.split(" ")[p.name.split(" ").length - 1];
    btn.innerHTML = `
      <span class="tab-dot"></span>
      <span>${shortName}</span>
    `;
    btn.addEventListener("click", () => {
      if (!isKioskMode) {
        playSound('switch');
        selectPersona(p.id);
      }
    });
    personaNav.appendChild(btn);
  });
}

// Switch Active Persona
function selectPersona(personaId) {
  currentPersonaId = personaId;
  document.body.setAttribute("data-theme", personaId);
  stopSpeaking();

  document.querySelectorAll(".persona-tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-id") === personaId);
  });

  const persona = personas.find(p => p.id === personaId) || personas[0];
  if (!persona) return;

  if (isKioskMode) {
    kioskTitle.textContent = `EXHIBIT // ${persona.name.toUpperCase()}`;
  }

  // Update Hologram Chamber
  holoEra.textContent = persona.era || "";
  dossierName.textContent = persona.name;
  dossierTitle.textContent = persona.title;
  dossierQuote.textContent = persona.quote || "";
  dossierWords.textContent = `${(persona.wordCount || 0).toLocaleString()} words`;
  channelName.textContent = `${personaId.toUpperCase()}_DIRECT`;
  userInput.placeholder = `Ask ${persona.name}...`;

  // Large high-resolution portrait
  avatarPhoto.src = `/images/${personaId}_large.jpg`;
  if (holoHudCode) {
    holoHudCode.textContent = `HOLO // ${persona.name.toUpperCase()} // 1080p`;
  }

  // Render Floating Inventions & Life Works
  renderFloatingArtifacts(persona.artifacts || []);

  // Render Milestones Timeline
  renderMilestones(persona.milestones || []);

  // Render Category Filter Tabs
  activeCategory = "All";
  renderCategoryFilter(persona.categories || {});

  // Render Starter Prompts
  renderPrompts(persona.starters || []);

  // Initialize or restore conversation history
  if (chatHistories[personaId].length === 0) {
    const welcome = INITIAL_GREETINGS[personaId] || "Transmission link established. Ask your question.";
    chatHistories[personaId].push({
      role: "persona",
      text: welcome,
      chunks: [],
      timestamp: formatTime(new Date())
    });
  }

  renderChatHistory();
}

// Render Floating Holographic Artifacts Layer
function renderFloatingArtifacts(artifacts) {
  if (!floatingArtifactsLayer) return;
  floatingArtifactsLayer.innerHTML = "";
  if (!artifacts || artifacts.length === 0) return;

  artifacts.forEach((artifact, index) => {
    const card = document.createElement("div");
    card.className = `floating-artifact-card ${index % 2 === 0 ? "pos-left" : "pos-right"}`;
    card.title = `${artifact.title} (${artifact.year}) — Click to ask persona`;
    card.innerHTML = `
      <div class="floating-card-thumb">
        <img src="${artifact.image}" alt="${escapeHtml(artifact.title)}" loading="lazy" />
        <span class="floating-card-badge">${artifact.year}</span>
      </div>
      <div class="floating-card-meta">
        <strong class="floating-card-title">${escapeHtml(artifact.title)}</strong>
        <span class="floating-card-tag">${escapeHtml(artifact.tag)}</span>
        <span class="floating-card-hint">
          <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          <span>Ask Work</span>
        </span>
      </div>
    `;
    card.addEventListener("click", () => {
      playSound('click');
      userInput.value = artifact.prompt || `Explain the breakthrough and historical impact of your work on ${artifact.title} (${artifact.year}).`;
      handleSendMessage();
    });
    floatingArtifactsLayer.appendChild(card);
  });
}

// Render Milestones Timeline Track
function renderMilestones(milestones) {
  milestonesTrack.innerHTML = "";
  milestones.forEach(m => {
    const chip = document.createElement("div");
    chip.className = "milestone-chip";
    chip.title = m.event;
    chip.innerHTML = `
      <span class="milestone-year">${m.year}</span>
      <span class="milestone-text">${m.event}</span>
    `;
    chip.addEventListener("click", () => {
      playSound('click');
      userInput.value = `Tell me about what happened in ${m.year}: ${m.event}`;
      handleSendMessage();
    });
    milestonesTrack.appendChild(chip);
  });
}

// Render Category Filter Tabs
function renderCategoryFilter(categories) {
  categoryFilterBar.innerHTML = "";
  const allBtn = document.createElement("button");
  allBtn.className = `category-pill ${activeCategory === 'All' ? 'active' : ''}`;
  allBtn.textContent = "All Topics";
  allBtn.addEventListener("click", () => {
    playSound('click');
    activeCategory = "All";
    document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
    allBtn.classList.add("active");
    const currentPersona = personas.find(p => p.id === currentPersonaId);
    renderPrompts(currentPersona?.starters || []);
  });
  categoryFilterBar.appendChild(allBtn);

  Object.keys(categories).forEach(cat => {
    const pill = document.createElement("button");
    pill.className = `category-pill ${activeCategory === cat ? 'active' : ''}`;
    pill.textContent = cat;
    pill.addEventListener("click", () => {
      playSound('click');
      activeCategory = cat;
      document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      renderPrompts(categories[cat] || []);
    });
    categoryFilterBar.appendChild(pill);
  });
}

// Render Suggestions Chips
function renderPrompts(prompts) {
  promptsContainer.innerHTML = '<span class="prompts-tag">PROMPTS:</span>';
  prompts.forEach(text => {
    const chip = document.createElement("button");
    chip.className = "prompt-chip";
    chip.textContent = text;
    chip.addEventListener("click", () => {
      playSound('click');
      userInput.value = text;
      handleSendMessage();
    });
    promptsContainer.appendChild(chip);
  });
}

// Render Chat Flow
function renderChatHistory() {
  messagesContainer.innerHTML = "";
  const history = chatHistories[currentPersonaId] || [];
  history.forEach((msg, idx) => {
    appendMessageToDOM(msg, idx);
  });
  scrollToBottom();
}

// Append single message to DOM
function appendMessageToDOM(msg, index, isStreaming = false) {
  const isPersona = msg.role === "persona";
  const row = document.createElement("div");
  row.className = `msg-row ${isPersona ? "persona" : "user"}`;
  if (isStreaming) row.id = `msg-row-${index}`;

  const personaMeta = personas.find(p => p.id === currentPersonaId);
  const name = isPersona ? (personaMeta ? personaMeta.name : "Hologram") : "You";

  let toolsHtml = "";
  if (isPersona) {
    const hasChunks = msg.chunks && msg.chunks.length > 0;
    toolsHtml = `
      <div class="msg-tools">
        <button class="bubble-btn tts-replay-btn" data-text="${encodeURIComponent(msg.text)}" title="Listen to spoken audio">
          ${SVG_ICONS.play}
          <span>Play Voice</span>
        </button>
        <button class="bubble-btn copy-msg-btn" data-text="${encodeURIComponent(msg.text)}" title="Copy text to clipboard">
          ${SVG_ICONS.copy}
          <span>Copy</span>
        </button>
        ${hasChunks ? `
          <button class="bubble-btn inspect-chunks-btn" data-index="${index}" title="View grounded ChromaDB text chunks">
            ${SVG_ICONS.context}
            <span>Grounded Context (${msg.chunks.length})</span>
          </button>
        ` : ''}
      </div>
    `;
  }

  const avatarImg = isPersona 
    ? `<img src="/images/${currentPersonaId}_avatar.jpg" alt="${name}" />`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

  row.innerHTML = `
    <div class="msg-avatar">${avatarImg}</div>
    <div class="msg-bubble-wrap">
      <div class="msg-meta">
        <strong>${name}</strong>
        <span>${msg.timestamp}</span>
      </div>
      <div class="msg-bubble" id="bubble-content-${index}">${escapeHtml(msg.text)}</div>
      ${toolsHtml}
    </div>
  `;

  // Attach listeners
  const replayBtn = row.querySelector(".tts-replay-btn");
  if (replayBtn) {
    replayBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      playSound('click');
      speakText(decodeURIComponent(replayBtn.getAttribute("data-text")));
    });
  }

  const copyBtn = row.querySelector(".copy-msg-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      playSound('click');
      navigator.clipboard.writeText(decodeURIComponent(copyBtn.getAttribute("data-text")));
      showToast("Copied to clipboard!");
    });
  }

  const inspectBtn = row.querySelector(".inspect-chunks-btn");
  if (inspectBtn) {
    inspectBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      playSound('click');
      openDrawerWithChunks(msg.chunks);
    });
  }

  messagesContainer.appendChild(row);
  return row;
}

// Send Message Handler
async function handleSendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  playSound('transmit');

  const userMsg = {
    role: "user",
    text: text,
    timestamp: formatTime(new Date())
  };
  chatHistories[currentPersonaId].push(userMsg);
  appendMessageToDOM(userMsg, chatHistories[currentPersonaId].length - 1);
  userInput.value = "";
  userInput.style.height = "auto";
  scrollToBottom();

  setLoadingState(true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        persona: currentPersonaId,
        question: text
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }

    const data = await res.json();
    latestContextChunks = data.context_chunks || [];
    chunkCountBadge.textContent = latestContextChunks.length;

    playSound('receive');
    removeTypingBubble();

    const replyIndex = chatHistories[currentPersonaId].length;
    const personaReply = {
      role: "persona",
      text: data.answer,
      chunks: latestContextChunks,
      timestamp: formatTime(new Date())
    };
    chatHistories[currentPersonaId].push(personaReply);

    // 1. Immediately trigger live avatar talking and voice audio (Zero delay)
    if (ttsEnabled) {
      speakText(data.answer);
    }

    // 2. Stream typewriter rapidly in parallel so text appears instantly
    streamTypewriterReply(personaReply, replyIndex);

  } catch (err) {
    console.error("Chat error:", err);
    removeTypingBubble();
    const errorMsg = {
      role: "persona",
      text: `[Transmission Anomaly]: ${err.message}`,
      chunks: [],
      timestamp: formatTime(new Date())
    };
    chatHistories[currentPersonaId].push(errorMsg);
    appendMessageToDOM(errorMsg, chatHistories[currentPersonaId].length - 1);
    scrollToBottom();
  } finally {
    setLoadingState(false);
  }
}

// Fast Real-Time Typewriter Streaming (Snappy & Responsive)
function streamTypewriterReply(personaReply, index) {
  return new Promise((resolve) => {
    const row = appendMessageToDOM({ ...personaReply, text: "" }, index, true);
    const bubble = document.getElementById(`bubble-content-${index}`);
    if (!bubble) {
      resolve();
      return;
    }

    const fullText = personaReply.text;
    let charIdx = 0;
    const step = 8; // Ultra-fast chunk per tick

    const interval = setInterval(() => {
      charIdx += step;
      if (charIdx >= fullText.length) {
        bubble.innerHTML = escapeHtml(fullText);
        clearInterval(interval);
        scrollToBottom();
        resolve();
      } else {
        bubble.innerHTML = escapeHtml(fullText.slice(0, charIdx)) + '<span class="streaming-cursor"></span>';
        scrollToBottom();
      }
    }, 8);
  });
}

// Typing Indicator Bubble
function setLoadingState(loading) {
  sendBtn.disabled = loading;
  if (loading) {
    holoStatus.textContent = "RETRIEVING & COMPUTING...";
    waveform.classList.add("active");

    const typingRow = document.createElement("div");
    typingRow.className = "msg-row persona typing-indicator-row";
    typingRow.id = "typing-bubble";
    typingRow.innerHTML = `
      <div class="msg-avatar"><img src="/images/${currentPersonaId}_avatar.jpg" alt="Thinking" /></div>
      <div class="msg-bubble-wrap">
        <div class="msg-bubble">
          <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      </div>
    `;
    messagesContainer.appendChild(typingRow);
    scrollToBottom();
  } else {
    holoStatus.textContent = "TRANSMITTING ACTIVE";
    if (!isSpeaking) {
      waveform.classList.remove("active");
    }
  }
}

function removeTypingBubble() {
  const bubble = document.getElementById("typing-bubble");
  if (bubble) bubble.remove();
}

// ==========================================================================
// Live Talking Avatar Animation & Speech
// ==========================================================================

function startTalkingAnimation() {
  isSpeaking = true;
  personaAvatarWrapper.classList.add("talking");
  stopSpeakingBtn.classList.remove("hidden");
  waveform.classList.add("active");
}

function stopTalkingAnimation() {
  isSpeaking = false;
  personaAvatarWrapper.classList.remove("talking");
  stopSpeakingBtn.classList.add("hidden");
  waveform.classList.remove("active");
}

function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  stopTalkingAnimation();
}

function getBestVoiceForPersona(personaId) {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (!voices || voices.length === 0) return null;

  const currentPersona = personas.find(p => p.id === personaId);
  const keywords = currentPersona?.voiceSettings?.voiceKeywords || [];

  for (const kw of keywords) {
    const match = voices.find(v => 
      v.lang.toLowerCase().includes(kw) || v.name.toLowerCase().includes(kw)
    );
    if (match) return match;
  }

  if (personaId === "kalam") {
    const indianVoice = voices.find(v => v.lang.startsWith("en-IN") || v.lang.startsWith("hi-IN"));
    if (indianVoice) return indianVoice;
  }

  return voices.find(v => v.lang.startsWith("en") && (v.name.includes("Male") || v.name.includes("Natural"))) 
    || voices.find(v => v.lang.startsWith("en")) 
    || voices[0];
}

function speakText(text) {
  if (!('speechSynthesis' in window) || !ttsEnabled) return;

  stopSpeaking();
  const cleanText = text.replace(/[*#_`]/g, '');
  const utterance = new SpeechSynthesisUtterance(cleanText);

  const personaMeta = personas.find(p => p.id === currentPersonaId);
  const voiceCfg = personaMeta?.voiceSettings || {};

  utterance.voice = getBestVoiceForPersona(currentPersonaId);
  utterance.pitch = voiceCfg.pitch || 1.0;
  utterance.rate = (voiceCfg.rate || 1.0) * currentSpeedMultiplier;

  utterance.onstart = () => {
    startTalkingAnimation();
  };

  utterance.onend = () => {
    stopTalkingAnimation();
  };

  utterance.onerror = () => {
    stopTalkingAnimation();
  };

  window.speechSynthesis.speak(utterance);
}

// Voice Engine Pre-warming (Eliminates speech initialization lag)
function prewarmSpeechVoices() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.getVoices();
  }
}

if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = prewarmSpeechVoices;
  prewarmSpeechVoices();
  window.addEventListener('click', prewarmSpeechVoices, { once: true });
  window.addEventListener('keydown', prewarmSpeechVoices, { once: true });
}

// Speech-to-Text (Microphone Dictation)
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micBtn.style.display = "none";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add("listening");
    recStatus.classList.remove("hidden");
    playSound('click');
  };

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    userInput.value = transcript;
    handleSendMessage();
  };

  recognition.onerror = (e) => {
    console.warn("Speech error:", e.error);
    isRecording = false;
    micBtn.classList.remove("listening");
    recStatus.classList.add("hidden");
  };

  recognition.onend = () => {
    isRecording = false;
    micBtn.classList.remove("listening");
    recStatus.classList.add("hidden");
  };
}

// Grounded Context Drawer Controls
function openDrawerWithChunks(chunks) {
  drawerContent.innerHTML = "";
  if (!chunks || chunks.length === 0) {
    drawerContent.innerHTML = `
      <div class="empty-state-notice">
        <p>No text chunks found for this message.</p>
      </div>
    `;
  } else {
    chunks.forEach((chunk, i) => {
      const card = document.createElement("div");
      card.className = "chunk-card";
      card.innerHTML = `
        <div class="chunk-card-header">
          <span class="chunk-badge">CHUNK #${i + 1}</span>
          <span class="chunk-chars">${chunk.length} characters</span>
        </div>
        <div class="chunk-body">${escapeHtml(chunk)}</div>
      `;
      drawerContent.appendChild(card);
    });
  }

  contextDrawer.classList.remove("hidden");
  drawerBackdrop.classList.remove("hidden");
}

function closeDrawer() {
  contextDrawer.classList.add("hidden");
  drawerBackdrop.classList.add("hidden");
}

// Network Routing & QR Studio
let networkInfo = {
  local_ip: "127.0.0.1",
  local_url: "http://127.0.0.1:8000",
  tunnel_url: null,
  recommended: window.location.origin
};
let selectedQrNetworkMode = "tunnel"; // "tunnel" or "lan"

async function fetchNetworkInfo() {
  try {
    const res = await fetch("/api/network-info");
    if (res.ok) {
      networkInfo = await res.json();
    }
  } catch (err) {
    console.warn("Could not fetch network info:", err);
  }
}

function getActiveQrBaseUrl() {
  if (selectedQrNetworkMode === "tunnel" && networkInfo.tunnel_url) {
    return networkInfo.tunnel_url;
  }
  if (selectedQrNetworkMode === "lan" && networkInfo.local_url) {
    return networkInfo.local_url;
  }
  return networkInfo.recommended || window.location.origin;
}

// Render QR Badges Studio
async function openQrStudio() {
  playSound('click');
  await fetchNetworkInfo();
  setupQrNetworkControls();
  renderQrPlacards();
  qrStudioModal.classList.remove("hidden");
}

function setupQrNetworkControls() {
  const tunnelBtn = document.getElementById("net-mode-tunnel");
  const lanBtn = document.getElementById("net-mode-lan");
  const lanText = document.getElementById("lan-btn-text");

  if (lanText && networkInfo.local_ip) {
    lanText.textContent = `Local Wi-Fi (${networkInfo.local_ip})`;
  }

  if (tunnelBtn && !tunnelBtn.dataset.bound) {
    tunnelBtn.dataset.bound = "true";
    tunnelBtn.addEventListener("click", () => {
      playSound('click');
      selectedQrNetworkMode = "tunnel";
      tunnelBtn.classList.add("active");
      if (lanBtn) lanBtn.classList.remove("active");
      renderQrPlacards();
    });
  }

  if (lanBtn && !lanBtn.dataset.bound) {
    lanBtn.dataset.bound = "true";
    lanBtn.addEventListener("click", () => {
      playSound('click');
      selectedQrNetworkMode = "lan";
      lanBtn.classList.add("active");
      if (tunnelBtn) tunnelBtn.classList.remove("active");
      renderQrPlacards();
    });
  }
}

function renderQrPlacards() {
  const baseUrl = getActiveQrBaseUrl();
  const targetDisplay = document.getElementById("active-target-url-text");
  if (targetDisplay) targetDisplay.textContent = baseUrl;

  qrCardsContainer.innerHTML = "";
  personas.forEach(p => {
    const card = document.createElement("div");
    card.className = "exhibit-qr-card";
    const kioskUrl = `${baseUrl}/?persona=${p.id}&kiosk=true`;
    const qrEndpoint = `/api/qr/${p.id}?base_url=${encodeURIComponent(baseUrl)}`;

    card.innerHTML = `
      <div class="card-photo-wrap">
        <img src="/images/${p.id}_avatar.jpg" alt="${p.name}" />
      </div>
      <h3 class="card-persona-name">${p.name}</h3>
      <span class="card-persona-title">${p.title}</span>
      
      <div class="card-qr-img-wrap">
        <img src="${qrEndpoint}" alt="Scan QR for ${p.name}" />
      </div>
      
      <span class="card-scan-label">SCAN TO CONVERSE (LOCKED TO ${p.name.split(" ")[p.name.split(" ").length - 1].toUpperCase()})</span>
      <div class="card-qr-target-url" title="${kioskUrl}">${kioskUrl}</div>
      
      <div class="card-actions-row">
        <button class="card-copy-btn" data-url="${kioskUrl}" title="Copy direct phone link">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <span>Copy Link</span>
        </button>
        <a href="${qrEndpoint}" download="${p.id}_hologram_qr.png" class="card-download-btn" title="Download QR PNG image">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <span>Download PNG</span>
        </a>
      </div>
    `;

    const copyBtn = card.querySelector(".card-copy-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", () => {
        playSound('click');
        navigator.clipboard.writeText(kioskUrl);
        showToast("Phone link copied to clipboard!");
      });
    }

    qrCardsContainer.appendChild(card);
  });
}

function closeQrStudio() {
  qrStudioModal.classList.add("hidden");
}

// Surprise Me / Quantum Warp Surprise Question
function handleSurpriseWarp() {
  playSound('switch');

  // Trigger Quantum Warp visual flash
  if (warpFlare) {
    warpFlare.classList.remove("hidden");
    warpFlare.classList.remove("active");
    void warpFlare.offsetWidth; // force reflow
    warpFlare.classList.add("active");
    setTimeout(() => {
      warpFlare.classList.add("hidden");
      warpFlare.classList.remove("active");
    }, 1100);
  }

  const persona = personas.find(p => p.id === currentPersonaId) || personas[0];
  if (!persona) return;

  const surprises = persona.surprises || [
    "What is the most profound revelation or mystery from your life's work?",
    "What unexpected passion or secret hobby shaped your thinking beyond science?",
    "If you could send a singular message to today's generation, what would it be?"
  ];

  // Pick a random surprise question
  const randomIndex = Math.floor(Math.random() * surprises.length);
  const surprisePrompt = surprises[randomIndex];

  showToast(`Temporal Archive: Uncovering secret inquiry...`);
  userInput.value = surprisePrompt;
  handleSendMessage();
}

// Open Artifacts Codex Modal
function openArtifactsCodex() {
  playSound('click');
  const persona = personas.find(p => p.id === currentPersonaId) || personas[0];
  if (!persona) return;

  if (codexModalTitle) {
    codexModalTitle.textContent = `${persona.name} — Life Works & Technical Schematics`;
  }
  if (codexModalSubtitle) {
    codexModalSubtitle.textContent = `Explore authentic blueprints, patents, and historical discoveries from the ${persona.name.split(" ")[0]} archive.`;
  }

  codexGridContainer.innerHTML = "";
  const artifacts = persona.artifacts || [];

  if (artifacts.length === 0) {
    codexGridContainer.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 2rem;">
        No cataloged schematics available for this persona.
      </div>
    `;
  } else {
    artifacts.forEach(art => {
      const card = document.createElement("div");
      card.className = "codex-item-card";
      card.innerHTML = `
        <div class="codex-img-wrap">
          <img src="${art.image}" alt="${escapeHtml(art.title)}" />
          <div class="codex-img-overlay"></div>
          <div class="codex-badge-row">
            <span class="codex-year-tag">${art.year}</span>
            <span class="codex-category-tag">${escapeHtml(art.tag)}</span>
          </div>
        </div>
        <div class="codex-content">
          <h3>${escapeHtml(art.title)}</h3>
          <p>${escapeHtml(art.summary)}</p>
          <button class="codex-ask-btn" data-prompt="${encodeURIComponent(art.prompt)}">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            <span>Ask ${persona.name.split(" ")[0]} to Explain</span>
          </button>
        </div>
      `;

      const askBtn = card.querySelector(".codex-ask-btn");
      if (askBtn) {
        askBtn.addEventListener("click", () => {
          const prompt = decodeURIComponent(askBtn.getAttribute("data-prompt"));
          closeArtifactsCodex();
          playSound('click');
          userInput.value = prompt;
          handleSendMessage();
        });
      }

      codexGridContainer.appendChild(card);
    });
  }

  artifactsCodexModal.classList.remove("hidden");
}

function closeArtifactsCodex() {
  artifactsCodexModal.classList.add("hidden");
}

// Export Chat Transcript
function exportTranscript() {
  playSound('click');
  const history = chatHistories[currentPersonaId] || [];
  const currentPersona = personas.find(p => p.id === currentPersonaId);
  const name = currentPersona?.name || currentPersonaId.toUpperCase();

  let transcript = `========================================================\n`;
  transcript += `HOLO PERSONA HISTORICAL SESSION TRANSCRIPT\n`;
  transcript += `Persona: ${name} (${currentPersona?.era || ''})\n`;
  transcript += `Date: ${new Date().toLocaleString()}\n`;
  transcript += `========================================================\n\n`;

  history.forEach(m => {
    const sender = m.role === 'user' ? 'YOU' : name.toUpperCase();
    transcript += `[${m.timestamp}] ${sender}:\n${m.text}\n\n`;
  });

  const blob = new Blob([transcript], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${currentPersonaId}_chat_transcript.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Transcript exported!");
}

// Fullscreen Toggle
function toggleFullscreen() {
  playSound('click');
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
}

// Toast notification helper
function showToast(text) {
  toastMsg.textContent = text;
  toastMsg.classList.remove("hidden");
  setTimeout(() => {
    toastMsg.classList.add("hidden");
  }, 2200);
}

// Verify Operator Passcode
async function handleVerifyPin() {
  const pin = operatorPinInput.value.trim();
  if (!pin) {
    pinErrorMsg.textContent = "Please enter the passcode.";
    return;
  }

  try {
    const res = await fetch("/api/verify-pin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: pin })
    });

    const data = await res.json();
    if (data.success) {
      playSound('receive');
      sessionStorage.setItem("master_auth", "true");
      isMasterAuthenticated = true;
      accessGateModal.classList.add("hidden");
      selectPersona("einstein");
    } else {
      pinErrorMsg.textContent = data.detail || "Incorrect Passcode. Try '1879'.";
    }
  } catch (err) {
    pinErrorMsg.textContent = "Verification failed. Check server connection.";
  }
}

// Event Listeners Setup
function setupEventListeners() {
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 100) + "px";
  });

  sendBtn.addEventListener("click", handleSendMessage);

  stopSpeakingBtn.addEventListener("click", () => {
    playSound('click');
    stopSpeaking();
  });

  micBtn.addEventListener("click", () => {
    if (!recognition) {
      alert("Speech recognition is not supported by your browser.");
      return;
    }
    if (isRecording) {
      recognition.stop();
    } else {
      try {
        recognition.start();
      } catch (err) {
        console.warn(err);
      }
    }
  });

  ttsToggleBtn.addEventListener("click", () => {
    playSound('click');
    ttsEnabled = !ttsEnabled;
    ttsLabel.textContent = `Voice: ${ttsEnabled ? "ON" : "OFF"}`;
    if (!ttsEnabled) stopSpeaking();
  });

  sfxToggleBtn.addEventListener("click", () => {
    sfxEnabled = !sfxEnabled;
    sfxToggleBtn.querySelector(".btn-text").textContent = `SFX: ${sfxEnabled ? "ON" : "OFF"}`;
    playSound('click');
  });

  document.querySelectorAll(".speed-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      playSound('click');
      document.querySelectorAll(".speed-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentSpeedMultiplier = parseFloat(btn.getAttribute("data-speed")) || 1.0;
    });
  });

  exportChatBtn.addEventListener("click", exportTranscript);
  fullscreenBtn.addEventListener("click", toggleFullscreen);

  memoryToggleBtn.addEventListener("click", () => {
    playSound('click');
    openDrawerWithChunks(latestContextChunks);
  });

  closeDrawerBtn.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);

  qrStudioBtn.addEventListener("click", openQrStudio);
  closeQrModalBtn.addEventListener("click", closeQrStudio);

  if (surpriseBtn) surpriseBtn.addEventListener("click", handleSurpriseWarp);
  if (artifactsCodexBtn) artifactsCodexBtn.addEventListener("click", openArtifactsCodex);
  if (closeCodexModalBtn) closeCodexModalBtn.addEventListener("click", closeArtifactsCodex);
  if (artifactsCodexModal) {
    artifactsCodexModal.addEventListener("click", (e) => {
      if (e.target === artifactsCodexModal) closeArtifactsCodex();
    });
  }

  // 3D Interactive Parallax for Grand Portrait
  if (grandPortraitContainer && personaAvatarWrapper) {
    grandPortraitContainer.addEventListener("mousemove", (e) => {
      const rect = grandPortraitContainer.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      personaAvatarWrapper.style.transform = `perspective(850px) rotateY(${x * 14}deg) rotateX(${-y * 14}deg) translateY(-4px) scale(1.02)`;
    });

    grandPortraitContainer.addEventListener("mouseleave", () => {
      personaAvatarWrapper.style.transform = "";
    });
  }

  verifyPinBtn.addEventListener("click", handleVerifyPin);
  operatorPinInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleVerifyPin();
  });

  clearChatBtn.addEventListener("click", () => {
    playSound('click');
    if (confirm(`Clear chat history with ${personas.find(p=>p.id===currentPersonaId)?.name || 'this persona'}?`)) {
      chatHistories[currentPersonaId] = [];
      const welcome = INITIAL_GREETINGS[currentPersonaId];
      chatHistories[currentPersonaId].push({
        role: "persona",
        text: welcome,
        chunks: [],
        timestamp: formatTime(new Date())
      });
      renderChatHistory();
    }
  });
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

window.addEventListener("DOMContentLoaded", init);
