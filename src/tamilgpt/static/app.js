(() => {
  "use strict";

  const API = "/api/v1";
  const STORAGE = {
    lang: "tamilgpt_lang",
    profile: "tamilgpt_profile",
    key: "tamilgpt_api_key",
  };

  const I18N = {
    ta: {
      brandTagline: "தமிழ்நாட்டுக்கான வழிகாட்டி",
      navLabel: "சேவைகள்",
      navChat: "பேச்சு",
      navSchemes: "அரசு திட்டங்கள்",
      navCareers: "வேலை & தொழில்",
      navFinance: "கடன் & நிதி",
      navHealth: "உடல்நலம்",
      navEmergency: "அவசர உதவி",
      sideDocs: "அறிவுத் தளம்",
      sideSchemes: "திட்டங்கள்",
      sideNote: "அனைத்து பதில்களும் ஆதாரங்களுடன். இது அரசு ஆலோசனை அல்ல.",
      heroEyebrow: "தமிழ் முதன்மை AI",
      heroTitle: "உங்கள் வாழ்க்கைக்கு தேவையான வழிகாட்டி, தமிழில்.",
      heroSubtitle: "அரசு திட்டங்கள், வேலை, கடன், உடல்நலம், சட்ட உதவி, விவசாயம் — ஒரே இடத்தில், ஆதாரங்களுடன், உங்கள் மொழியில்.",
      chipFree: "இலவசம்",
      chipSources: "ஆதாரங்களுடன்",
      chipLanguages: "தமிழ் · Tanglish · English",
      statSchemes: "அரசு திட்டங்கள்",
      statCareers: "தொழில் வழிகள்",
      statHelplines: "உதவி எண்கள்",
      statSectors: "துறைகள்",
      quickLabel: "விரைவு கேள்விகள்",
      composerLabel: "உங்கள் கேள்வி",
      composerHint: "Enter அனுப்ப · Shift+Enter புதிய வரி",
      send: "அனுப்பு",
      footerNote: "TamilGPT 2.0 · தமிழ்நாட்டுக்காக உருவாக்கப்பட்டது",
      profileTitle: "உங்கள் சுயவிவரம்",
      profileHint: "துல்லியமான பதில்களுக்கு. இது உங்கள் சாதனத்தில் மட்டுமே சேமிக்கப்படும்.",
      age: "வயது",
      gender: "பாலினம்",
      select: "தேர்வு",
      female: "பெண்",
      male: "ஆண்",
      other: "மற்றவர்",
      income: "மாத வருமானம் (₹)",
      occupation: "தொழில்",
      district: "மாவட்டம்",
      education: "கல்வி",
      family: "குடும்ப அளவு",
      save: "சேமி",
      clear: "அழி",
      emergencyTitle: "அவசர உதவி",
      emergencyHint: "உயிருக்கு ஆபத்து என்றால் உடனே அழையுங்கள்.",
      howTitle: "எப்படி வேலை செய்கிறது?",
      howStep1: "உங்கள் கேள்வி தமிழ், Tanglish அல்லது English-ல் புரிந்துகொள்ளப்படும்.",
      howStep2: "சரிபார்க்கப்பட்ட அறிவுத் தளத்தில் இருந்து தகவல் தேடப்படும்.",
      howStep3: "தகுதி, ஆவணங்கள், மூலங்கள் ஆகியவற்றுடன் தெளிவான பதில் கிடைக்கும்.",
      sourceNote: "மூலங்கள்: தமிழ்நாடு அரசு, மத்திய அரசு, e-Sevai மற்றும் அதிகாரப்பூர்வ இணையதளங்கள்.",
      apiTitle: "API key தேவை",
      apiHint: "இந்த சர்வர் பாதுகாக்கப்பட்டுள்ளது. உங்கள் API key-ஐ உள்ளிடுங்கள். இது இந்த தாவலில் மட்டுமே சேமிக்கப்படும்.",
      close: "மூடு",
      statusOnline: "இணைக்கப்பட்டது",
      statusOffline: "இணைப்பு இல்லை",
      thinking: "யோசிக்கிறேன்…",
      errorTitle: "மன்னிக்கவும், ஏதோ தவறு நடந்தது.",
      copy: "நகலெடு",
      copied: "நகலெடுக்கப்பட்டது",
      feedbackThanks: "நன்றி!",
      profileSaved: "சுயவிவரம் சேமிக்கப்பட்டது",
      profileCleared: "சுயவிவரம் அழிக்கப்பட்டது",
      voiceUnsupported: "இந்த உலாவியில் குரல் உள்ளீடு இல்லை.",
      listening: "கேட்கிறேன்…",
      welcome: "வணக்கம்! நான் TamilGPT 2.0. அரசு திட்டங்கள், வேலை, கடன், உடல்நலம், சட்ட உதவி, விவசாயம் பற்றி தமிழில் கேளுங்கள். வயது, வருமானம், மாவட்டம் போன்ற விவரங்களைச் சொன்னால் இன்னும் துல்லியமாகப் பதில் தருவேன்.",
      grounded: "ஆதாரங்களுடன்",
      offlineMode: "ஆஃப்லைன்",
      you: "நீங்கள்",
      assistant: "TamilGPT",
    },
    en: {
      brandTagline: "A guide for Tamil Nadu",
      navLabel: "Services",
      navChat: "Chat",
      navSchemes: "Government schemes",
      navCareers: "Jobs & careers",
      navFinance: "Loans & money",
      navHealth: "Health",
      navEmergency: "Emergency help",
      sideDocs: "Knowledge base",
      sideSchemes: "Schemes",
      sideNote: "Every answer cites sources. This is not official government advice.",
      heroEyebrow: "Tamil-first AI",
      heroTitle: "The guidance you need, in your language.",
      heroSubtitle: "Government schemes, jobs, loans, health, legal aid and farming — in one place, with sources, in Tamil, Tanglish or English.",
      chipFree: "Free",
      chipSources: "Sources included",
      chipLanguages: "Tamil · Tanglish · English",
      statSchemes: "Schemes",
      statCareers: "Career paths",
      statHelplines: "Helplines",
      statSectors: "Sectors",
      quickLabel: "Quick questions",
      composerLabel: "Your question",
      composerHint: "Enter to send · Shift+Enter for a new line",
      send: "Send",
      footerNote: "TamilGPT 2.0 · Built for Tamil Nadu",
      profileTitle: "Your profile",
      profileHint: "For precise answers. Stored only on your device.",
      age: "Age",
      gender: "Gender",
      select: "Select",
      female: "Female",
      male: "Male",
      other: "Other",
      income: "Monthly income (₹)",
      occupation: "Occupation",
      district: "District",
      education: "Education",
      family: "Family size",
      save: "Save",
      clear: "Clear",
      emergencyTitle: "Emergency help",
      emergencyHint: "If life is in danger, call immediately.",
      howTitle: "How it works",
      howStep1: "Your question is understood in Tamil, Tanglish or English.",
      howStep2: "Verified knowledge is retrieved from the curated knowledge base.",
      howStep3: "You get a clear answer with eligibility, documents and sources.",
      sourceNote: "Sources: Government of Tamil Nadu, Government of India, e-Sevai and official portals.",
      apiTitle: "API key required",
      apiHint: "This server is protected. Enter your API key. It is stored only in this tab.",
      close: "Close",
      statusOnline: "Connected",
      statusOffline: "Offline",
      thinking: "Thinking…",
      errorTitle: "Sorry, something went wrong.",
      copy: "Copy",
      copied: "Copied",
      feedbackThanks: "Thanks!",
      profileSaved: "Profile saved",
      profileCleared: "Profile cleared",
      voiceUnsupported: "Voice input is not available in this browser.",
      listening: "Listening…",
      welcome: "Vanakkam! I am TamilGPT 2.0. Ask me about government schemes, jobs, loans, health, legal aid or farming in Tamil, Tanglish or English. Share your age, income and district for a more precise answer.",
      grounded: "Grounded",
      offlineMode: "Offline mode",
      you: "You",
      assistant: "TamilGPT",
    },
    tanglish: {
      brandTagline: "Tamil Nadu-ku vazhikatti",
      navLabel: "Sevaigal",
      navChat: "Pesu",
      navSchemes: "Thittangal",
      navCareers: "Velai & Thozhil",
      navFinance: "Kadan & Panam",
      navHealth: "Udalnalam",
      navEmergency: "Avasara udhavi",
      sideDocs: "Arivu thoguthi",
      sideSchemes: "Thittangal",
      sideNote: "Ellam sources-oda. Ithu government advice illa.",
      heroEyebrow: "Tamil-first AI",
      heroTitle: "Ungal vazhkai-ku thevaiyana vazhikatti, Tamil-la.",
      heroSubtitle: "Government schemes, velai, kadan, udalnalam, legal help, vivasayam — ore idathula, sources-oda, ungal mozhiyila.",
      chipFree: "Free",
      chipSources: "Sources-oda",
      chipLanguages: "Tamil · Tanglish · English",
      statSchemes: "Thittangal",
      statCareers: "Velai vazhigal",
      statHelplines: "Udhavi numbers",
      statSectors: "Thuraigal",
      quickLabel: "Quick kelvigal",
      composerLabel: "Ungal kelvi",
      composerHint: "Enter anuppu · Shift+Enter new line",
      send: "Anuppu",
      footerNote: "TamilGPT 2.0 · Tamil Nadu-ku",
      profileTitle: "Ungal profile",
      profileHint: "Precise answer-ku. Ungal device-la mattum save aagum.",
      age: "Vayasu",
      gender: "Paal",
      select: "Thervu",
      female: "Penn",
      male: "Aan",
      other: "Mathavanga",
      income: "Monthly varumanam (₹)",
      occupation: "Thozhil",
      district: "Mavattam",
      education: "Kalvi",
      family: "Kudumbam",
      save: "Save",
      clear: "Clear",
      emergencyTitle: "Avasara udhavi",
      emergencyHint: "Uyiruku aabathu na udane call pannunga.",
      howTitle: "Eppadi velai seigirathu?",
      howStep1: "Ungal kelvi Tamil, Tanglish illa English-la purinjikkapadum.",
      howStep2: "Verified arivu thoguthi-la irundhu thagaval thedapadum.",
      howStep3: "Eligibility, documents, sources-oda clear answer kidaikkum.",
      sourceNote: "Sources: Tamil Nadu government, central government, e-Sevai and official portals.",
      apiTitle: "API key venum",
      apiHint: "Indha server protected. Ungal API key podunga. Ithu indha tab-la mattum save aagum.",
      close: "Moodu",
      statusOnline: "Connected",
      statusOffline: "Offline",
      thinking: "Yosikiren…",
      errorTitle: "Sorry, edho thappu aayiduchu.",
      copy: "Copy",
      copied: "Copied",
      feedbackThanks: "Nandri!",
      profileSaved: "Profile saved",
      profileCleared: "Profile cleared",
      voiceUnsupported: "Indha browser-la voice input illa.",
      listening: "Kekkiren…",
      welcome: "Vanakkam! Naan TamilGPT 2.0. Government schemes, velai, kadan, udalnalam, legal help, vivasayam pathi Tamil-la kelunga. Vayasu, varumanam, mavattam sonna innum precise-a answer tharuven.",
      grounded: "Grounded",
      offlineMode: "Offline mode",
      you: "Neenga",
      assistant: "TamilGPT",
    },
  };

  const QUICK = {
    ta: [
      "நெல்லுக்கு எந்த உரம் சரி?",
      "எனக்கு 35 வயது, பெண், மாத வருமானம் ₹18,000. எந்த திட்டம் கிடைக்கும்?",
      "₹5 லட்சம் கடன் எடுத்தால் EMI எவ்வளவு?",
      "காய்ச்சல் 4 நாட்கள் ஆகிறது, என்ன செய்ய வேண்டும்?",
      "வேலை தேடுகிறேன், B.Com படித்திருக்கேன்",
      "விதவை ஓய்வூதியம் எப்படி விண்ணப்பிப்பது?",
    ],
    en: [
      "Which fertiliser is right for paddy?",
      "I am 35, a woman, earning ₹18,000 a month. Which schemes can I get?",
      "What is the EMI for a ₹5 lakh loan?",
      "I have had fever for 4 days. What should I do?",
      "I am looking for a job. I have a B.Com degree.",
      "How do I apply for the widow pension?",
    ],
    tanglish: [
      "Nelluku entha urum sari?",
      "Enaku 35 vayasu, penn, monthly ₹18,000. Entha thittam kidaikkum?",
      "₹5 lakh kadan edutha EMI evlo?",
      "Kaichal 4 naal aagirathu, enna pannanum?",
      "Velai theduren, B.Com padithiruken",
      "Vidhavai pension eppadi apply panrathu?",
    ],
  };

  const NAV_PROMPTS = {
    schemes: {
      ta: "எனக்கு எந்த அரசு திட்டம் கிடைக்கும்?",
      en: "Which government schemes can I get?",
      tanglish: "Enaku entha government thittam kidaikkum?",
    },
    careers: {
      ta: "எனக்கு ஏற்ற வேலை வாய்ப்புகள் என்ன?",
      en: "What careers fit my profile?",
      tanglish: "Enaku etha velai vaaipu irukku?",
    },
    finance: {
      ta: "₹5 லட்சம் கடன் எடுத்தால் EMI எவ்வளவு?",
      en: "What is the EMI for a ₹5 lakh loan?",
      tanglish: "₹5 lakh kadan edutha EMI evlo?",
    },
    health: {
      ta: "உடல்நலம் பற்றி ஆலோசனை வேண்டும்",
      en: "I need health guidance",
      tanglish: "Udalnalam pathi advice venum",
    },
  };

  const state = {
    lang: "ta",
    messages: [],
    busy: false,
    retryText: "",
    lastSector: null,
    recognition: null,
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  function t(key) {
    return I18N[state.lang]?.[key] ?? I18N.en[key] ?? key;
  }

  function apiLang() {
    if (state.lang === "ta") return "ta";
    if (state.lang === "en") return "en";
    return "auto";
  }

  function safeStorageGet(store, key) {
    try { return store.getItem(key); } catch { return null; }
  }

  function safeStorageSet(store, key, value) {
    try { store.setItem(key, value); } catch { /* ignore */ }
  }

  function safeStorageRemove(store, key) {
    try { store.removeItem(key); } catch { /* ignore */ }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function inlineMarkdown(text) {
    let out = text;
    out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/[^\s)]*)\)/g, (_, label, url) => (
      `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`
    ));
    out = out.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
    return out;
  }

  function renderMarkdown(raw) {
    const lines = escapeHtml(raw).split("\n");
    let html = "";
    let list = null;
    const closeList = () => {
      if (list) {
        html += `</${list}>`;
        list = null;
      }
    };
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) { closeList(); continue; }
      if (trimmed === "---") { closeList(); html += "<hr>"; continue; }
      let match = trimmed.match(/^###\s+(.*)$/);
      if (match) { closeList(); html += `<h3>${inlineMarkdown(match[1])}</h3>`; continue; }
      match = trimmed.match(/^##\s+(.*)$/);
      if (match) { closeList(); html += `<h4>${inlineMarkdown(match[1])}</h4>`; continue; }
      match = trimmed.match(/^[-*]\s+(.*)$/);
      if (match) {
        if (list !== "ul") { closeList(); html += "<ul>"; list = "ul"; }
        html += `<li>${inlineMarkdown(match[1])}</li>`;
        continue;
      }
      match = trimmed.match(/^\d+\.\s+(.*)$/);
      if (match) {
        if (list !== "ol") { closeList(); html += "<ol>"; list = "ol"; }
        html += `<li>${inlineMarkdown(match[1])}</li>`;
        continue;
      }
      closeList();
      if (/^_.+_$/.test(trimmed)) {
        html += `<p><em>${inlineMarkdown(trimmed.slice(1, -1))}</em></p>`;
      } else {
        html += `<p>${inlineMarkdown(trimmed)}</p>`;
      }
    }
    closeList();
    return html;
  }

  function svgIcon(name) {
    return `<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-${name}"/></svg>`;
  }

  function iconButton(label, icon, extra = "") {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "icon-btn";
    btn.title = label;
    btn.setAttribute("aria-label", label);
    btn.innerHTML = svgIcon(icon);
    if (extra) btn.dataset.action = extra;
    return btn;
  }

  function scrollToBottom() {
    const log = $("#chat-log");
    if (log) log.scrollTop = log.scrollHeight;
  }

  function appendMessage(role, text, data = {}) {
    const log = $("#chat-log");
    if (!log) return null;
    const msg = document.createElement("div");
    msg.className = `msg ${role}`;
    msg.dataset.raw = text;
    if (data.requestId) msg.dataset.requestId = data.requestId;
    if (data.sector) msg.dataset.sector = data.sector;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = role === "user" ? "நீ" : "த";

    const body = document.createElement("div");
    body.className = "bubble";
    if (role === "user") {
      body.textContent = text;
    } else {
      body.innerHTML = renderMarkdown(text);
    }

    if (data.citations?.length) {
      const citations = document.createElement("div");
      citations.className = "citations";
      data.citations.forEach((citation, index) => {
        const item = document.createElement(citation.url ? "a" : "div");
        item.className = "citation";
        if (citation.url) {
          item.href = citation.url;
          item.target = "_blank";
          item.rel = "noopener noreferrer";
        }
        const badge = document.createElement("span");
        badge.className = "cite-index";
        badge.textContent = String(index + 1);
        const title = document.createElement("span");
        title.textContent = citation.title || citation.source || "Source";
        item.append(badge, title);
        if (citation.source) {
          const source = document.createElement("span");
          source.className = "cite-source";
          source.textContent = citation.source;
          item.append(source);
        }
        citations.append(item);
      });
      body.append(citations);
    }

    if (data.disclaimers?.length) {
      const note = document.createElement("div");
      note.className = "disclaimer";
      note.textContent = data.disclaimers.join(" ");
      body.append(note);
    }

    if (data.followups?.length) {
      const followups = document.createElement("div");
      followups.className = "followups";
      data.followups.forEach((question) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "followup";
        button.textContent = question;
        button.addEventListener("click", () => sendMessage(question));
        followups.append(button);
      });
      body.append(followups);
    }

    if (role === "assistant" && !data.welcome) {
      const meta = document.createElement("div");
      meta.className = "msg-meta";
      if (data.provider) {
        const pill = document.createElement("span");
        pill.className = "meta-pill";
        pill.textContent = data.provider === "offline" ? t("offlineMode") : data.provider;
        meta.append(pill);
      }
      if (data.grounded) {
        const pill = document.createElement("span");
        pill.className = "meta-pill";
        pill.textContent = t("grounded");
        meta.append(pill);
      }
      if (meta.childElementCount) body.append(meta);

      const actions = document.createElement("div");
      actions.className = "msg-actions";
      const copyBtn = iconButton(t("copy"), "copy");
      copyBtn.addEventListener("click", () => copyText(text));
      const up = iconButton("Helpful", "up");
      const down = iconButton("Not helpful", "down");
      up.addEventListener("click", () => sendFeedback(up, 5, msg));
      down.addEventListener("click", () => sendFeedback(down, 2, msg));
      actions.append(copyBtn, up, down);
      body.append(actions);
    }

    msg.append(avatar, body);
    log.append(msg);
    scrollToBottom();
    return msg;
  }

  function appendTyping() {
    const log = $("#chat-log");
    if (!log) return null;
    const msg = document.createElement("div");
    msg.className = "msg assistant";
    msg.dataset.typing = "true";
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "த";
    const body = document.createElement("div");
    body.className = "bubble";
    const typing = document.createElement("span");
    typing.className = "typing";
    typing.setAttribute("aria-label", t("thinking"));
    typing.innerHTML = "<span></span><span></span><span></span>";
    body.append(typing);
    msg.append(avatar, body);
    log.append(msg);
    scrollToBottom();
    return msg;
  }

  function toast(message) {
    const el = $("#toast");
    if (!el) return;
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => el.classList.remove("show"), 2600);
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      toast(t("copied"));
    } catch {
      const area = document.createElement("textarea");
      area.value = text;
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.append(area);
      area.select();
      try { document.execCommand("copy"); toast(t("copied")); } catch { /* ignore */ }
      area.remove();
    }
  }

  async function apiFetch(path, options = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    const key = safeStorageGet(sessionStorage, STORAGE.key);
    if (key) headers["X-API-Key"] = key;
    try {
      const response = await fetch(`${API}${path}`, { ...options, headers, signal: controller.signal });
      if (response.status === 401) {
        openApiModal();
        const error = new Error("unauthorized");
        error.code = "unauthorized";
        throw error;
      }
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data?.error?.message || `Request failed (${response.status})`;
        const error = new Error(message);
        error.code = data?.error?.code || "request_failed";
        error.requestId = response.headers.get("X-Request-ID");
        throw error;
      }
      return data;
    } catch (error) {
      if (error.name === "AbortError") throw new Error("Request timed out. Please try again.");
      throw error;
    } finally {
      clearTimeout(timer);
    }
  }

  function setBusy(busy) {
    state.busy = busy;
    const send = $("#send-btn");
    const shell = $(".chat-shell");
    if (send) send.disabled = busy;
    if (shell) shell.setAttribute("aria-busy", busy ? "true" : "false");
  }

  async function sendMessage(rawText, options = {}) {
    const text = String(rawText || "").trim();
    if (!text || state.busy) return;
    const input = $("#message-input");
    if (input) { input.value = ""; resizeInput(); updateCharCount(); }
    closeDrawers();

    if (!options.retry) {
      appendMessage("user", text);
      state.messages.push({ role: "user", content: text });
    }

    setBusy(true);
    const typing = appendTyping();
    const history = state.messages.slice(0, -1).slice(-16);
    const payload = {
      message: text,
      language: apiLang(),
      history,
      profile: collectProfile(),
    };

    try {
      const data = await apiFetch("/chat", { method: "POST", body: JSON.stringify(payload) });
      typing?.remove();
      appendMessage("assistant", data.reply, {
        citations: data.citations,
        disclaimers: data.disclaimers,
        followups: data.followups,
        provider: data.provider,
        grounded: data.grounded,
        requestId: data.request_id,
        sector: data.intent?.sector,
      });
      state.messages.push({ role: "assistant", content: data.reply });
      state.messages = state.messages.slice(-16);
      state.lastSector = data.intent?.sector || null;
      state.retryText = "";
    } catch (error) {
      typing?.remove();
      if (error.code === "unauthorized") {
        state.retryText = text;
        toast(t("apiTitle"));
      } else {
        appendMessage("assistant", `${t("errorTitle")}\n\n${error.message}`);
      }
    } finally {
      setBusy(false);
      if (input) input.focus();
    }
  }

  function collectProfile() {
    const form = $("#profile-form");
    if (!form) return null;
    const data = new FormData(form);
    const profile = {};
    for (const [key, value] of data.entries()) {
      const text = String(value).trim();
      if (!text) continue;
      if (["age", "monthly_income", "family_size"].includes(key)) {
        const number = Number(text);
        if (Number.isFinite(number)) profile[key] = number;
      } else {
        profile[key] = text;
      }
    }
    return Object.keys(profile).length ? profile : null;
  }

  function loadProfile() {
    const raw = safeStorageGet(localStorage, STORAGE.profile);
    if (!raw) return;
    try {
      const profile = JSON.parse(raw);
      for (const [key, value] of Object.entries(profile)) {
        const field = $(`#${key}`);
        if (field) field.value = value ?? "";
      }
    } catch { /* ignore */ }
  }

  function saveProfile(event) {
    event.preventDefault();
    const profile = collectProfile() || {};
    safeStorageSet(localStorage, STORAGE.profile, JSON.stringify(profile));
    const note = $("#save-note");
    if (note) {
      note.textContent = t("profileSaved");
      setTimeout(() => { note.textContent = ""; }, 2500);
    }
  }

  function clearProfile() {
    const form = $("#profile-form");
    if (form) form.reset();
    safeStorageRemove(localStorage, STORAGE.profile);
    const note = $("#save-note");
    if (note) {
      note.textContent = t("profileCleared");
      setTimeout(() => { note.textContent = ""; }, 2500);
    }
  }

  async function sendFeedback(button, rating, messageEl) {
    button.classList.add("active");
    try {
      await apiFetch("/feedback", {
        method: "POST",
        body: JSON.stringify({
          rating,
          sector: messageEl?.dataset.sector || state.lastSector,
          language: apiLang() === "auto" ? null : apiLang(),
          message_id: messageEl?.dataset.requestId || null,
        }),
      });
      toast(t("feedbackThanks"));
    } catch { /* feedback is best effort */ }
  }

  function renderQuick() {
    const container = $("#quick-prompts");
    if (!container) return;
    container.innerHTML = "";
    (QUICK[state.lang] || QUICK.en).forEach((question) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.textContent = question;
      chip.addEventListener("click", () => sendMessage(question));
      container.append(chip);
    });
  }

  function renderWelcome() {
    appendMessage("assistant", t("welcome"), { welcome: true });
  }

  function clearChat() {
    const log = $("#chat-log");
    if (log) log.innerHTML = "";
    state.messages = [];
    state.retryText = "";
    renderWelcome();
    $("#message-input")?.focus();
  }

  async function loadMeta() {
    try {
      const data = await apiFetch("/meta");
      const docs = $("#side-docs");
      const schemes = $("#side-schemes");
      if (docs) docs.textContent = `${data.knowledge.documents}+`;
      if (schemes) schemes.textContent = `${data.knowledge.schemes}`;
      const setStat = (id, value) => {
        const el = $(`#${id}`);
        if (el && value !== undefined) el.textContent = String(value);
      };
      setStat("stat-schemes", data.knowledge.schemes);
      setStat("stat-careers", data.knowledge.careers);
      setStat("stat-helplines", data.knowledge.helplines);
      setStat("stat-sectors", data.knowledge.sectors?.length);
    } catch { /* metadata is optional */ }
  }

  async function loadHelplines() {
    const container = $("#helpline-list");
    if (!container) return;
    container.innerHTML = "";
    let lines = [];
    try {
      lines = await apiFetch(`/helplines?language=${state.lang === "ta" ? "ta" : "en"}`);
    } catch {
      lines = [
        { number: "112", name: "National emergency", description: "Police, fire, ambulance" },
        { number: "108", name: "Ambulance", description: "Emergency medical help" },
        { number: "1098", name: "Child helpline", description: "Children in danger" },
        { number: "181", name: "Women helpline", description: "Women in distress" },
        { number: "104", name: "Health advice", description: "Medical guidance" },
        { number: "14416", name: "Tele-MANAS", description: "Mental health support" },
      ];
    }
    const preferred = ["112", "108", "1098", "181", "104", "14416"];
    const byNumber = new Map(lines.map((line) => [line.number, line]));
    const selected = preferred.map((number) => byNumber.get(number)).filter(Boolean);
    const items = (selected.length ? selected : lines.slice(0, 6));
    items.forEach((line) => {
      const link = document.createElement("a");
      link.className = "helpline";
      link.href = `tel:${line.number}`;
      const number = document.createElement("span");
      number.className = "num";
      number.textContent = line.number;
      const name = document.createElement("span");
      name.className = "name";
      name.textContent = line.name;
      if (line.description) {
        const small = document.createElement("small");
        small.textContent = line.description;
        name.append(small);
      }
      link.append(number, name);
      container.append(link);
    });
  }

  function applyLanguage() {
    document.documentElement.lang = state.lang === "ta" ? "ta" : "en";
    document.title = state.lang === "ta"
      ? "TamilGPT 2.0 — தமிழ் வாழ்க்கை வழிகாட்டி"
      : "TamilGPT 2.0 — Tamil-first life guidance";
    $$("[data-i18n]").forEach((el) => {
      const key = el.dataset.i18n;
      if (key) el.textContent = t(key);
    });
    $$(".lang-btn").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.lang === state.lang ? "true" : "false");
    });
    const input = $("#message-input");
    if (input) {
      input.placeholder = state.lang === "ta"
        ? "உங்கள் கேள்வியை எழுதுங்கள்…"
        : state.lang === "en"
          ? "Ask your question…"
          : "Ungal kelviya ezhuthunga…";
    }
    const statusText = $("#status-text");
    if (statusText) statusText.textContent = navigator.onLine ? t("statusOnline") : t("statusOffline");
    renderQuick();
    loadHelplines();
    if (!state.messages.length) {
      const log = $("#chat-log");
      if (log) log.innerHTML = "";
      renderWelcome();
    }
  }

  function setLanguage(lang) {
    if (!I18N[lang]) return;
    state.lang = lang;
    safeStorageSet(localStorage, STORAGE.lang, lang);
    applyLanguage();
  }

  function openApiModal() {
    const modal = $("#api-modal");
    if (modal) modal.classList.add("open");
    const input = $("#api-key-input");
    if (input) setTimeout(() => input.focus(), 50);
  }

  function closeApiModal() {
    $("#api-modal")?.classList.remove("open");
  }

  function saveApiKey() {
    const input = $("#api-key-input");
    const value = input ? input.value.trim() : "";
    if (value) safeStorageSet(sessionStorage, STORAGE.key, value);
    closeApiModal();
    if (state.retryText) {
      const text = state.retryText;
      state.retryText = "";
      sendMessage(text, { retry: true });
    }
  }

  function closeDrawers() {
    $("#sidebar")?.classList.remove("open");
    $("#rail")?.classList.remove("open");
    $("#menu-btn")?.setAttribute("aria-expanded", "false");
    $("#profile-btn")?.setAttribute("aria-expanded", "false");
  }

  function toggleDrawer(element, button) {
    if (!element) return;
    const open = element.classList.toggle("open");
    button?.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function updateCharCount() {
    const input = $("#message-input");
    const counter = $("#char-count");
    if (!input || !counter) return;
    counter.textContent = `${input.value.length} / 2000`;
  }

  function resizeInput() {
    const input = $("#message-input");
    if (!input) return;
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 170)}px`;
  }

  function setupVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const button = $("#mic-btn");
    if (!button) return;
    if (!SpeechRecognition) {
      button.disabled = true;
      button.title = t("voiceUnsupported");
      return;
    }
    button.addEventListener("click", () => {
      if (state.recognition) {
        state.recognition.stop();
        return;
      }
      const recognition = new SpeechRecognition();
      recognition.lang = state.lang === "ta" ? "ta-IN" : "en-IN";
      recognition.interimResults = true;
      recognition.continuous = false;
      state.recognition = recognition;
      button.classList.add("listening");
      toast(t("listening"));
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0].transcript)
          .join(" ");
        const input = $("#message-input");
        if (input) {
          input.value = transcript;
          resizeInput();
          updateCharCount();
        }
      };
      recognition.onerror = () => toast(t("voiceUnsupported"));
      recognition.onend = () => {
        button.classList.remove("listening");
        state.recognition = null;
      };
      try { recognition.start(); } catch { button.classList.remove("listening"); state.recognition = null; }
    });
  }

  function handleNav(action) {
    if (action === "chat") {
      closeDrawers();
      $("#message-input")?.focus();
      return;
    }
    if (action === "emergency") {
      $("#rail")?.classList.add("open");
      $("#profile-btn")?.setAttribute("aria-expanded", "true");
      toast("112 · 108 · 1098 · 181");
      return;
    }
    const prompt = NAV_PROMPTS[action]?.[state.lang] || NAV_PROMPTS[action]?.en;
    if (prompt) sendMessage(prompt);
  }

  function setupEvents() {
    $$(".lang-btn").forEach((button) => {
      button.addEventListener("click", () => setLanguage(button.dataset.lang));
    });
    $$(".nav-item").forEach((button) => {
      button.addEventListener("click", () => handleNav(button.dataset.action));
    });
    $("#profile-form")?.addEventListener("submit", saveProfile);
    $("#clear-profile")?.addEventListener("click", clearProfile);
    $("#composer")?.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = $("#message-input");
      sendMessage(input ? input.value : "");
    });
    const input = $("#message-input");
    input?.addEventListener("input", () => {
      resizeInput();
      updateCharCount();
    });
    input?.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        $("#composer")?.requestSubmit();
      }
    });
    $("#new-chat")?.addEventListener("click", clearChat);
    $("#menu-btn")?.addEventListener("click", () => toggleDrawer($("#sidebar"), $("#menu-btn")));
    $("#profile-btn")?.addEventListener("click", () => toggleDrawer($("#rail"), $("#profile-btn")));
    $("#api-key-save")?.addEventListener("click", saveApiKey);
    $("#api-key-close")?.addEventListener("click", closeApiModal);
    $("#api-key-input")?.addEventListener("keydown", (event) => {
      if (event.key === "Enter") { event.preventDefault(); saveApiKey(); }
    });
    $("#api-modal")?.addEventListener("click", (event) => {
      if (event.target === $("#api-modal")) closeApiModal();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeDrawers();
        closeApiModal();
      }
    });
    window.addEventListener("online", () => {
      $("#status-dot")?.classList.remove("offline");
      const status = $("#status-text");
      if (status) status.textContent = t("statusOnline");
    });
    window.addEventListener("offline", () => {
      $("#status-dot")?.classList.add("offline");
      const status = $("#status-text");
      if (status) status.textContent = t("statusOffline");
    });
  }

  function init() {
    const savedLang = safeStorageGet(localStorage, STORAGE.lang);
    if (savedLang && I18N[savedLang]) state.lang = savedLang;
    loadProfile();
    setupEvents();
    setupVoice();
    applyLanguage();
    loadMeta();
    updateCharCount();
    resizeInput();
    const status = $("#status-text");
    if (status) status.textContent = navigator.onLine ? t("statusOnline") : t("statusOffline");
    if (!navigator.onLine) $("#status-dot")?.classList.add("offline");
    $("#message-input")?.focus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
