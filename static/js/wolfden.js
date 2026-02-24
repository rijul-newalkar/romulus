/* ============================================================
   WOLF DEN — Romulus Dashboard Controller
   ============================================================ */

(function () {
    'use strict';

    // ── Configuration ──────────────────────────────────────────
    const API_BASE = '';  // Same origin
    const POLL_INTERVAL = 5000;   // 5 seconds
    const FEED_MAX_ITEMS = 50;

    // ── State ──────────────────────────────────────────────────
    const state = {
        connected: false,
        wolfState: 'idle',   // idle | working | dreaming | alert
        status: null,
        fitness: null,
        rules: [],
        traces: [],
        incidents: [],
        dreamReports: [],
        feedItems: [],
        uptimeBase: 0,
        uptimeStart: Date.now(),
        isDreaming: false,
    };

    // ── DOM References ─────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    // ── API Helpers ────────────────────────────────────────────
    async function apiGet(path) {
        const res = await fetch(`${API_BASE}${path}`);
        if (!res.ok) throw new Error(`GET ${path}: ${res.status}`);
        return res.json();
    }

    async function apiPost(path, body) {
        const res = await fetch(`${API_BASE}${path}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`POST ${path}: ${res.status}`);
        return res.json();
    }

    // ── Formatting Helpers ─────────────────────────────────────
    function formatUptime(totalSeconds) {
        const d = Math.floor(totalSeconds / 86400);
        const h = Math.floor((totalSeconds % 86400) / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = Math.floor(totalSeconds % 60);

        if (d > 0) return `${d}d ${h}h ${m}m`;
        if (h > 0) return `${h}h ${m}m ${s}s`;
        return `${m}m ${s}s`;
    }

    function formatTime(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const now = new Date();
        const diff = (now - d) / 1000;

        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    }

    function pct(val) {
        return `${Math.round((val || 0) * 100)}%`;
    }

    // ── Uptime Ticker ──────────────────────────────────────────
    function startUptimeTicker() {
        const el = $('#uptime-value');
        if (!el) return;

        setInterval(() => {
            const elapsed = (Date.now() - state.uptimeStart) / 1000;
            const total = state.uptimeBase + elapsed;
            el.textContent = formatUptime(total);
        }, 1000);
    }

    // ── Connection Status ──────────────────────────────────────
    function updateConnection(online) {
        state.connected = online;
        const dot = $('#connection-dot');
        const text = $('#connection-text');
        if (dot) {
            dot.className = 'connection-dot ' + (online ? 'online' : 'offline');
        }
        if (text) {
            text.textContent = online ? 'Connected' : 'Offline';
        }
    }

    // ── Wolf State ─────────────────────────────────────────────
    function setWolfState(newState) {
        if (state.wolfState === newState) return;
        state.wolfState = newState;

        const container = $('#wolf');
        if (!container) return;

        container.className = 'wolf-container wolf-state-' + newState;

        // Update status badge
        const badge = $('#wolf-status-badge');
        if (badge) {
            const icons = { idle: '\u{1F43A}', working: '\u26A1', dreaming: '\u{1F319}', alert: '\u{1F6E1}\uFE0F' };
            const labels = { idle: 'Resting', working: 'Working', dreaming: 'Dreaming', alert: 'Alert!' };
            badge.innerHTML = `<span class="status-icon">${icons[newState] || icons.idle}</span> ${labels[newState] || labels.idle}`;
        }

        // Dream cloud
        const cloud = $('#dream-cloud');
        if (cloud) {
            cloud.classList.toggle('visible', newState === 'dreaming');
        }

        // Moon
        const moon = $('#window-moon');
        if (moon) {
            moon.classList.toggle('dreaming', newState === 'dreaming');
        }
    }

    // ── Score Rings ────────────────────────────────────────────
    function updateRing(id, value) {
        const circle = $(`#ring-${id}`);
        const text = $(`#ring-value-${id}`);
        if (!circle || !text) return;

        const radius = 32;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (value * circumference);

        circle.style.strokeDasharray = `${circumference}`;
        circle.style.strokeDashoffset = `${offset}`;
        text.textContent = pct(value);
    }

    // ── Bookshelf ──────────────────────────────────────────────
    function updateBookshelf(rulesCount) {
        const rows = $$('.bookshelf-row');
        if (!rows.length) return;

        const maxPerRow = 7;
        const totalMax = maxPerRow * rows.length;
        const display = Math.min(rulesCount, totalMax);

        let placed = 0;
        rows.forEach((row) => {
            row.innerHTML = '';
            const booksInRow = Math.min(maxPerRow, display - placed);
            for (let i = 0; i < booksInRow; i++) {
                const book = document.createElement('div');
                book.className = 'book';
                book.style.animationDelay = `${(placed + i) * 0.05}s`;
                row.appendChild(book);
                placed++;
            }
        });

        const label = $('#bookshelf-label');
        if (label) {
            label.textContent = `${rulesCount} rule${rulesCount !== 1 ? 's' : ''}`;
        }
    }

    // ── Campfire ───────────────────────────────────────────────
    function updateCampfire(fitness) {
        const glow = $('#campfire-glow');
        const flames = $$('.flame');
        if (!glow) return;

        glow.className = 'campfire-glow';
        if (fitness >= 0.7) {
            glow.classList.add('high');
        } else if (fitness < 0.3) {
            glow.classList.add('low');
        }

        // Scale flames based on fitness
        flames.forEach((f) => {
            const scale = 0.5 + (fitness * 0.5);
            f.style.transform = f.style.transform || '';
            f.style.opacity = 0.4 + (fitness * 0.6);
        });
    }

    // ── Trophies ───────────────────────────────────────────────
    function updateTrophies(statusData) {
        if (!statusData) return;
        const tasks = statusData.total_tasks || 0;
        const rules = statusData.rules_learned || 0;
        const trust = statusData.trust_score || 0;

        // First task, 10 tasks, 50 tasks, first rule, trust > 0.8
        const trophies = [
            { id: 'trophy-first', earned: tasks >= 1 },
            { id: 'trophy-10', earned: tasks >= 10 },
            { id: 'trophy-50', earned: tasks >= 50 },
            { id: 'trophy-rule', earned: rules >= 1 },
            { id: 'trophy-trust', earned: trust >= 0.8 },
        ];

        trophies.forEach(({ id, earned }) => {
            const el = $(`#${id}`);
            if (el) el.classList.toggle('earned', earned);
        });
    }

    // ── Stats Panel ────────────────────────────────────────────
    function updateStats(data) {
        if (!data) return;

        updateRing('trust', data.trust_score || 0);
        updateRing('fitness', data.composite_fitness || 0);

        const setVal = (id, val) => {
            const el = $(`#stat-${id}`);
            if (el) el.textContent = val;
        };

        setVal('tasks', data.total_tasks || 0);
        setVal('rules', data.rules_learned || 0);
        setVal('model', data.model || 'unknown');

        if (data.platform) {
            setVal('platform', `${data.platform.system || ''} ${data.platform.machine || ''}`);
        }

        // Success rate bar
        const rate = data.success_rate_7d || 0;
        const bar = $('#success-bar-fill');
        const barLabel = $('#success-rate-value');
        if (bar) bar.style.width = `${rate * 100}%`;
        if (barLabel) barLabel.textContent = pct(rate);
    }

    // ── Activity Feed ──────────────────────────────────────────
    function addFeedItem(type, text, time) {
        state.feedItems.unshift({ type, text, time: time || new Date().toISOString() });
        if (state.feedItems.length > FEED_MAX_ITEMS) {
            state.feedItems.length = FEED_MAX_ITEMS;
        }
    }

    function renderFeed() {
        const feed = $('#activity-feed');
        if (!feed) return;

        if (state.feedItems.length === 0) {
            feed.innerHTML = '<div class="feed-empty">No activity yet. The den is quiet...</div>';
            return;
        }

        feed.innerHTML = state.feedItems.map((item) => `
            <div class="feed-item">
                <div class="feed-dot ${item.type}"></div>
                <div class="feed-content">
                    <div class="feed-text" title="${escapeHtml(item.text)}">${escapeHtml(item.text)}</div>
                </div>
                <div class="feed-time">${formatTime(item.time)}</div>
            </div>
        `).join('');
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str || '';
        return div.innerHTML;
    }

    // ── Build Feed from Data ───────────────────────────────────
    function buildFeedFromData() {
        const items = [];

        // Traces
        if (state.traces && state.traces.length) {
            state.traces.forEach((t) => {
                items.push({
                    type: t.success ? 'success' : 'error',
                    text: `Task: ${t.task} — ${t.outcome || (t.success ? 'Success' : 'Failed')}`,
                    time: t.timestamp,
                    sortTime: new Date(t.timestamp).getTime(),
                });
            });
        }

        // Vigil incidents
        if (state.incidents && state.incidents.length) {
            state.incidents.forEach((inc) => {
                const reason = inc.reason || inc.category || 'Blocked';
                items.push({
                    type: 'vigil',
                    text: `Vigil: ${reason}${inc.task ? ' — ' + inc.task : ''}`,
                    time: inc.timestamp,
                    sortTime: new Date(inc.timestamp).getTime(),
                });
            });
        }

        // Dream reports
        if (state.dreamReports && state.dreamReports.length) {
            state.dreamReports.forEach((dr) => {
                items.push({
                    type: 'dream',
                    text: `Dream: ${dr.summary || `${dr.episodes_processed || 0} episodes processed`}`,
                    time: dr.date,
                    sortTime: new Date(dr.date).getTime(),
                });
            });
        }

        // Rules
        if (state.rules && state.rules.length) {
            state.rules.slice(0, 10).forEach((r) => {
                items.push({
                    type: 'rule',
                    text: `Rule learned: ${r.rule} (${pct(r.confidence)})`,
                    time: r.last_validated,
                    sortTime: new Date(r.last_validated).getTime(),
                });
            });
        }

        // Sort by time descending
        items.sort((a, b) => (b.sortTime || 0) - (a.sortTime || 0));

        state.feedItems = items.slice(0, FEED_MAX_ITEMS);
    }

    // ── Dream Cloud Text ───────────────────────────────────────
    function updateDreamCloud() {
        const text = $('#dream-cloud-text');
        if (!text) return;

        if (state.dreamReports && state.dreamReports.length) {
            const latest = state.dreamReports[0];
            text.textContent = latest.summary
                ? latest.summary.substring(0, 60) + (latest.summary.length > 60 ? '...' : '')
                : `${latest.episodes_processed || 0} episodes reviewed`;
        } else {
            text.textContent = 'No dreams yet...';
        }
    }

    // ── Data Fetching ──────────────────────────────────────────
    async function fetchStatus() {
        try {
            const data = await apiGet('/api/status');
            state.status = data;
            state.uptimeBase = data.uptime_seconds || 0;
            state.uptimeStart = Date.now();
            updateConnection(true);
            updateStats(data);
            updateTrophies(data);
            updateBookshelf(data.rules_learned || 0);
            updateCampfire(data.composite_fitness || 0);

            // Set header info
            const nameEl = $('#header-title');
            const verEl = $('#header-version');
            if (nameEl) nameEl.textContent = data.name || 'Romulus';
            if (verEl) verEl.textContent = `v${data.version || '0.1.0'}`;

        } catch (e) {
            console.warn('Status fetch failed:', e.message);
            updateConnection(false);
        }
    }

    async function fetchTraces() {
        try {
            state.traces = await apiGet('/api/traces?limit=30');
        } catch (e) {
            console.warn('Traces fetch failed:', e.message);
        }
    }

    async function fetchRules() {
        try {
            state.rules = await apiGet('/api/rules');
        } catch (e) {
            console.warn('Rules fetch failed:', e.message);
        }
    }

    async function fetchIncidents() {
        try {
            state.incidents = await apiGet('/api/vigil/incidents?hours=48');
        } catch (e) {
            console.warn('Incidents fetch failed:', e.message);
        }
    }

    async function fetchDreamReports() {
        try {
            state.dreamReports = await apiGet('/api/dream-reports');
        } catch (e) {
            console.warn('Dream reports fetch failed:', e.message);
        }
    }

    async function fetchAll() {
        await Promise.allSettled([
            fetchStatus(),
            fetchTraces(),
            fetchRules(),
            fetchIncidents(),
            fetchDreamReports(),
        ]);

        // Determine wolf state
        if (state.isDreaming) {
            setWolfState('dreaming');
        } else if (state.incidents && state.incidents.length > 0) {
            // Check if there are recent incidents (last 5 minutes)
            const now = Date.now();
            const recent = state.incidents.some((inc) => {
                const t = new Date(inc.timestamp).getTime();
                return (now - t) < 300000; // 5 minutes
            });
            if (recent) {
                setWolfState('alert');
            } else {
                setWolfState('idle');
            }
        } else {
            setWolfState('idle');
        }

        buildFeedFromData();
        renderFeed();
        updateDreamCloud();
    }

    // ── Actions ────────────────────────────────────────────────
    async function sendTask() {
        const input = $('#task-input');
        if (!input) return;

        const task = input.value.trim();
        if (!task) return;

        input.value = '';
        setWolfState('working');

        // Show response area
        const responsePanel = $('#response-panel');
        const responseContent = $('#response-content');
        const responseMeta = $('#response-meta');

        if (responseContent) responseContent.textContent = 'Thinking...';
        if (responseMeta) responseMeta.textContent = '';
        if (responsePanel) responsePanel.classList.add('visible');

        try {
            const result = await apiPost('/api/ask', { task });

            if (responseContent) {
                responseContent.textContent = result.response || 'No response.';
            }
            if (responseMeta) {
                const parts = [];
                if (result.confidence !== undefined) parts.push(`${pct(result.confidence)} confident`);
                if (result.tokens_used) parts.push(`${result.tokens_used} tokens`);
                if (result.latency_ms) parts.push(`${result.latency_ms}ms`);
                if (result.vigil_flags && result.vigil_flags.length) {
                    parts.push(`Vigil: ${result.vigil_flags.join(', ')}`);
                }
                responseMeta.textContent = parts.join(' | ');
            }

            addFeedItem(
                result.success !== false ? 'success' : 'error',
                `Task: ${task} — ${result.response ? result.response.substring(0, 80) : 'done'}`,
            );

        } catch (e) {
            if (responseContent) responseContent.textContent = `Error: ${e.message}`;
            addFeedItem('error', `Task failed: ${task} — ${e.message}`);
        }

        setWolfState('idle');
        renderFeed();

        // Refresh status after task
        setTimeout(() => fetchStatus(), 1000);
    }

    async function triggerDream() {
        const btn = $('#dream-btn');
        if (!btn || state.isDreaming) return;

        state.isDreaming = true;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Dreaming...';
        setWolfState('dreaming');

        const responsePanel = $('#response-panel');
        const responseContent = $('#response-content');
        const responseMeta = $('#response-meta');

        if (responseContent) responseContent.textContent = 'Entering dream cycle...';
        if (responseMeta) responseMeta.textContent = '';
        if (responsePanel) responsePanel.classList.add('visible');

        try {
            const report = await apiPost('/api/dream', {});

            if (responseContent) {
                responseContent.textContent = report.summary || 'Dream cycle complete.';
            }
            if (responseMeta) {
                const parts = [];
                parts.push(`${report.episodes_processed || 0} episodes`);
                parts.push(`${(report.new_rules_extracted || []).length} new rules`);
                parts.push(`${report.memories_pruned || 0} pruned`);
                responseMeta.textContent = parts.join(' | ');
            }

            addFeedItem('dream', `Dream: ${report.summary || 'Cycle complete'}`);

        } catch (e) {
            if (responseContent) responseContent.textContent = `Dream failed: ${e.message}`;
            addFeedItem('error', `Dream failed: ${e.message}`);
        }

        state.isDreaming = false;
        btn.disabled = false;
        btn.innerHTML = '\u{1F319} Trigger Dream Cycle';
        setWolfState('idle');
        renderFeed();

        // Refresh all data
        setTimeout(() => fetchAll(), 1000);
    }

    function wolfClicked() {
        // Quick status check animation
        const container = $('#wolf');
        if (!container) return;

        container.style.transform = 'translateX(-50%) scale(1.1)';
        setTimeout(() => {
            container.style.transform = 'translateX(-50%) scale(1)';
        }, 200);

        // Refresh status
        fetchStatus().then(() => {
            addFeedItem('info', 'Status check: all systems nominal');
            renderFeed();
        });
    }

    // ── Initialization ─────────────────────────────────────────
    function bindEvents() {
        // Send task
        const sendBtn = $('#send-btn');
        const taskInput = $('#task-input');
        if (sendBtn) sendBtn.addEventListener('click', sendTask);
        if (taskInput) {
            taskInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendTask();
                }
            });
        }

        // Dream
        const dreamBtn = $('#dream-btn');
        if (dreamBtn) dreamBtn.addEventListener('click', triggerDream);

        // Wolf click
        const wolf = $('#wolf');
        if (wolf) wolf.addEventListener('click', wolfClicked);
    }

    async function init() {
        bindEvents();
        startUptimeTicker();

        // Initial fetch
        await fetchAll();

        // Polling
        setInterval(fetchAll, POLL_INTERVAL);
    }

    // Wait for DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
