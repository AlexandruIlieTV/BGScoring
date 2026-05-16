async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  if (!response.ok) {
    throw new Error("Failed to load dashboard data.");
  }

  const payload = await response.json();
  renderSummary(payload.summary);
  renderHighlights(payload.highlights);
  renderTimeline(payload.timeline);
  renderGames(payload.top_games);
  renderPlayers(payload.top_players);
  renderSessions(payload.recent_sessions);
  setupInteractiveFilters(payload.player_names, payload.game_titles);
}

function renderSummary(summary) {
  const container = document.getElementById("summary-grid");
  const items = [
    ["Games tracked", summary.total_games, "Unique titles in the database"],
    ["Players", summary.total_players, "People in your board game circle"],
    ["Sessions", summary.total_sessions, "Logged play sessions so far"],
    ["Hours played", summary.total_hours, "Combined play time across sessions"],
    ["Avg. table", summary.average_table_size, "Average players per session"],
  ];

  container.innerHTML = items.map(([label, value, detail]) => `
    <article class="summary-card">
      <p class="summary-label">${label}</p>
      <p class="summary-value">${value}</p>
      <p class="summary-detail">${detail}</p>
    </article>
  `).join("");
}

function renderHighlights(highlights) {
  const latest = highlights.latest_session;
  const title = document.getElementById("latest-session-title");
  const meta = document.getElementById("latest-session-meta");

  if (!latest) {
    title.textContent = "No sessions yet";
    meta.textContent = "Add a few sessions and the dashboard will start telling a story.";
    return;
  }

  const sideNotes = [];

  if (highlights.busiest_game) {
    sideNotes.push(`Most played: ${highlights.busiest_game.title} (${highlights.busiest_game.sessions} sessions)`);
  }

  if (highlights.most_active_player) {
    sideNotes.push(`Most active player: ${highlights.most_active_player.name} (${highlights.most_active_player.plays} plays)`);
  }

  title.textContent = latest.title;
  meta.textContent = `${latest.session_date} | ${latest.players} players | ${latest.game_duration} min\n${sideNotes.join(" | ")}`;
}

function renderTimeline(timeline) {
  const container = document.getElementById("timeline");
  const maxSessions = Math.max(...timeline.map((item) => item.sessions), 1);

  container.innerHTML = timeline.map((item) => {
    const height = Math.max(16, Math.round((item.sessions / maxSessions) * 130));
    return `
      <article class="bar-card">
        <div class="bar-track">
          <div class="bar" style="height:${height}px"></div>
        </div>
        <div class="bar-label">${item.month}</div>
        <div class="bar-detail">${item.sessions} sessions | ${item.minutes} min</div>
      </article>
    `;
  }).join("");
}

function renderGames(games) {
  const container = document.getElementById("top-games");
  container.innerHTML = games.map((game) => `
    <article class="list-item">
      <strong>${escapeHtml(game.title)}</strong>
      <span>${game.sessions} sessions | ${game.total_minutes} min total</span>
      <span>${escapeHtml(game.game_theme || "Theme not set")} | ${escapeHtml(game.year_of_release || "Unknown year")}</span>
    </article>
  `).join("");
}

function renderPlayers(players) {
  const container = document.getElementById("top-players");
  container.innerHTML = players.map((player) => `
    <article class="list-item">
      <strong>${escapeHtml(player.name)}</strong>
      <span>${player.plays} plays | ${player.wins || 0} wins | ${player.win_rate || 0}% win rate</span>
      <span>Average score: ${player.average_score ?? "N/A"}</span>
    </article>
  `).join("");
}

function renderSessions(sessions) {
  const tbody = document.getElementById("recent-sessions");
  tbody.innerHTML = sessions.map((session) => `
    <tr>
      <td>${escapeHtml(session.title)}</td>
      <td>${session.session_date}</td>
      <td>${session.players}</td>
      <td>${session.game_duration} min</td>
      <td class="muted">${escapeHtml(session.roster || "No roster recorded")}</td>
    </tr>
  `).join("");
}

async function setupInteractiveFilters(playerNames, gameTitles) {
  const playerSelect = document.getElementById("player-select");
  const gameSelect = document.getElementById("game-select");

  playerSelect.innerHTML = playerNames.map((name) => `<option value="${escapeAttribute(name)}">${escapeHtml(name)}</option>`).join("");
  gameSelect.innerHTML = gameTitles.map((title) => `<option value="${escapeAttribute(title)}">${escapeHtml(title)}</option>`).join("");

  playerSelect.addEventListener("change", () => loadPlayerDetail(playerSelect.value));
  gameSelect.addEventListener("change", () => loadGameDetail(gameSelect.value));

  if (playerNames.length > 0) {
    await loadPlayerDetail(playerNames[0]);
  }

  if (gameTitles.length > 0) {
    await loadGameDetail(gameTitles[0]);
  }
}

async function loadPlayerDetail(playerName) {
  const response = await fetch(`/api/player?name=${encodeURIComponent(playerName)}`);
  const container = document.getElementById("player-detail");

  if (!response.ok) {
    container.innerHTML = `<p class="muted">Could not load player details.</p>`;
    return;
  }

  const payload = await response.json();
  const overview = payload.overview;
  const favorite = payload.favorite_game;
  const bestGame = payload.best_game;

  container.innerHTML = `
    <div class="metric-grid">
      <article class="metric-card">
        <span class="summary-label">Total plays</span>
        <strong>${overview.total_plays || 0}</strong>
      </article>
      <article class="metric-card">
        <span class="summary-label">Wins</span>
        <strong>${overview.wins || 0} (${overview.win_rate || 0}%)</strong>
      </article>
      <article class="metric-card">
        <span class="summary-label">Average score</span>
        <strong>${overview.average_score ?? "N/A"}</strong>
      </article>
      <article class="metric-card">
        <span class="summary-label">Best score</span>
        <strong>${overview.best_score ?? "N/A"}</strong>
      </article>
    </div>
    <div class="detail-stack">
      <div class="detail-note"><strong>Favorite game:</strong> ${favorite ? `${escapeHtml(favorite.title)} (${favorite.plays} plays)` : "Not enough data yet"}</div>
      <div class="detail-note"><strong>Best game:</strong> ${bestGame ? `${escapeHtml(bestGame.title)} with ${bestGame.win_rate}% win rate across ${bestGame.plays} plays` : "Requires at least 3 plays of the same game"}</div>
    </div>
    <div>
      <p class="section-kicker">Recent sessions</p>
      <div class="mini-table">
        ${renderPlayerSessions(payload.recent_sessions)}
      </div>
    </div>
    <div>
      <p class="section-kicker">Score records</p>
      <div class="mini-table">
        ${renderPlayerRecords(payload.score_records)}
      </div>
    </div>
  `;
}

async function loadGameDetail(gameTitle) {
  const response = await fetch(`/api/game?title=${encodeURIComponent(gameTitle)}`);
  const container = document.getElementById("game-detail");

  if (!response.ok) {
    container.innerHTML = `<p class="muted">Could not load game details.</p>`;
    return;
  }

  const payload = await response.json();
  const overview = payload.overview;
  const frequent = payload.most_frequent_player;
  const bestPlayer = payload.best_player;

  container.innerHTML = `
    <div class="metric-grid">
      <article class="metric-card">
        <span class="summary-label">Sessions</span>
        <strong>${overview.total_sessions || 0}</strong>
      </article>
      <article class="metric-card">
        <span class="summary-label">Average duration</span>
        <strong>${overview.average_duration ?? 0} min</strong>
      </article>
      <article class="metric-card">
        <span class="summary-label">Average score</span>
        <strong>${overview.average_score ?? "N/A"}</strong>
      </article>
      <article class="metric-card">
        <span class="summary-label">Player range</span>
        <strong>${overview.min_players}-${overview.max_players}</strong>
      </article>
    </div>
    <div class="detail-stack">
      <div class="detail-note"><strong>Theme:</strong> ${escapeHtml(overview.game_theme || "Not set")} | <strong>Year:</strong> ${escapeHtml(String(overview.year_of_release || "Unknown"))}</div>
      <div class="detail-note"><strong>Most frequent player:</strong> ${frequent ? `${escapeHtml(frequent.name)} (${frequent.plays} plays)` : "Not enough data yet"}</div>
      <div class="detail-note"><strong>Best player:</strong> ${bestPlayer ? `${escapeHtml(bestPlayer.name)} with ${bestPlayer.win_rate}% win rate across ${bestPlayer.plays} plays` : "Requires at least 3 plays"}</div>
    </div>
    <div>
      <p class="section-kicker">Leaderboard</p>
      <div class="mini-table">
        ${renderGameLeaderboard(payload.leaderboard)}
      </div>
    </div>
    <div>
      <p class="section-kicker">Recent sessions</p>
      <div class="mini-table">
        ${renderGameSessions(payload.recent_sessions)}
      </div>
    </div>
  `;
}

function renderPlayerSessions(sessions) {
  if (!sessions.length) {
    return `<div class="mini-row"><span class="muted">No sessions recorded.</span></div>`;
  }

  return sessions.map((session) => `
    <div class="mini-row">
      <strong>${escapeHtml(session.title)}</strong>
      <span>${session.session_date} | Score: ${session.player_score ?? "N/A"} | Standing: ${session.player_standing ?? "N/A"}</span>
    </div>
  `).join("");
}

function renderPlayerRecords(records) {
  if (!records.length) {
    return `<div class="mini-row"><span class="muted">No score records held yet.</span></div>`;
  }

  return records.map((record) => `
    <div class="mini-row">
      <strong>${escapeHtml(record.title)}</strong>
      <span>Record score: ${record.score}</span>
    </div>
  `).join("");
}

function renderGameLeaderboard(players) {
  if (!players.length) {
    return `<div class="mini-row"><span class="muted">No players recorded for this game.</span></div>`;
  }

  return players.map((player) => `
    <div class="mini-row">
      <strong>${escapeHtml(player.name)}</strong>
      <span>${player.plays} plays | ${player.wins || 0} wins | Avg. score: ${player.average_score ?? "N/A"}</span>
    </div>
  `).join("");
}

function renderGameSessions(sessions) {
  if (!sessions.length) {
    return `<div class="mini-row"><span class="muted">No sessions recorded for this game.</span></div>`;
  }

  return sessions.map((session) => `
    <div class="mini-row">
      <strong>${session.session_date}</strong>
      <span>${session.players} players | ${session.game_duration} min</span>
      <span class="muted">${escapeHtml(session.roster || "No roster recorded")}</span>
    </div>
  `).join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}

loadDashboard().catch((error) => {
  document.body.innerHTML = `<main class="page-shell"><section class="card"><h1>Dashboard unavailable</h1><p>${escapeHtml(error.message)}</p></section></main>`;
});
