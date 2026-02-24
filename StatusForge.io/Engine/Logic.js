let lastGame = "";
let sessionInterval;
let widgetFadeTimer = null; // Memory for the custom fade countdown
let startTime = 0;
let pollRate = 3000;

async function initializeWidget() {
    try {
        const url = 'http://127.0.0.1:5050/settings?nocache=' + new Date().getTime();
        const setRes = await fetch(url);
        const setJson = await setRes.json();
        pollRate = (setJson.widget_poll_rate || 3) * 1000;
    } catch(e) {}
    setInterval(pollEngine, pollRate);
    pollEngine();
}

async function pollEngine() {
    try {
        const url = 'http://127.0.0.1:5050/status?nocache=' + new Date().getTime();
        const res = await fetch(url);
        const data = await res.json();
        const w = document.getElementById("w"); 

        if (data.is_playing) {
            startTime = data.start_time;
            if (!sessionInterval) sessionInterval = setInterval(updateTimer, 1000);
            
            // Only trigger visual updates and timers if the game actually changes!
            if (data.game_title !== lastGame) {
                lastGame = data.game_title;
                
                // 1. Clear any active fade out timers
                if (widgetFadeTimer) clearTimeout(widgetFadeTimer);
                
                // 2. Bring the widget on screen
                w.style.opacity = "1";
                
                // 3. Update all metadata
                smoothTextUpdate("t", data.game_title); 
                smoothTextUpdate("r", data.release_date || "UNKNOWN");
                smoothTextUpdate("g", data.genre || "GAMING");
                smoothTextUpdate("p", data.publisher || "INDIE / UNKNOWN");
                
                if (data.cover_url) {
                    applyCoverArt(data.cover_url);
                } else {
                    applyCoverArt(''); // Blank if none found
                }
                
                // 4. Start the custom fade out countdown (if enabled in Dashboard)
                if (data.fade_timer > 0) {
                    widgetFadeTimer = setTimeout(() => {
                        w.style.opacity = "0";
                    }, data.fade_timer * 1000);
                }
            }
        } else {
            w.style.opacity = "0"; 
            lastGame = "";
            clearInterval(sessionInterval);
            sessionInterval = null;
            if (widgetFadeTimer) clearTimeout(widgetFadeTimer);
        }
    } catch(e) {}
}

function smoothTextUpdate(id, text) {
    const el = document.getElementById(id);
    if(!el) return;
    el.style.opacity = 0;
    setTimeout(() => { el.innerText = text; el.style.opacity = 1; }, 500); 
}

function applyCoverArt(url) {
    const cover = document.getElementById('a');
    if(!cover) return;
    cover.style.opacity = 0;
    setTimeout(() => {
        if(url) {
            cover.style.backgroundImage = `url('${url}')`;
            cover.style.backgroundColor = '#111';
        } else {
            cover.style.backgroundImage = 'none';
            cover.style.backgroundColor = '#050505'; // Fallback empty state
        }
        cover.style.opacity = 1;
    }, 500);
}

function updateTimer() {
    if (!startTime) return;
    const diff = Math.floor(Date.now() / 1000) - Math.floor(startTime);
    if (diff < 0) return;
    const h = String(Math.floor(diff / 3600)).padStart(2, '0');
    const m = String(Math.floor((diff % 3600) / 60)).padStart(2, '0');
    const s = String(diff % 60).padStart(2, '0');
    const el = document.getElementById("s"); 
    if (el) el.innerText = `${h}:${m}:${s}`;
}

initializeWidget();
