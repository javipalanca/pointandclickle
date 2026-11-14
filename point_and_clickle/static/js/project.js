/* Point & Clickle · game logic.
   Two modes, set by the page (games/views.py → game_config):
   - daily: today's game. Guesses in localStorage "guess_list" (with "daily_date"), counts in the player's stats
     ("stats") and in the game's guess distribution (POST /api/v1/game/<id>/hit/).
   - practice: a random game or a past day. Guesses in "practice_<game id>"; never touches the daily keys, the
     stats or the hit counter. Finished archive days are listed in "practice_days" for the archive page.
   Hints: from the 3rd wrong guess, one more clue per miss (year, developer, platform, genre: the ones the game has).
   At the end: how all players did with this game, and links to the game's pages in the Point and Click Museum.
   Analytics go through CLK.track (static/js/analytics.js). */
const MAX_GUESS = 6;
const GAMES_API = "/api/v1/game/";
const STREAK_ACHIEVEMENTS = [3, 7, 14, 30, 100];
const HINTS_FROM = 3;  // wrong guesses before the first hint

let G = { mode: "daily", kind: "daily", number: null, date: null, listKey: "guess_list" };
let fromList = false;
let gameData = null;   // the game's public data (developer, platform, year...), fetched once for hints and result

const track = (name, params) => {
    try { if (window.CLK) CLK.track(name, params); } catch (e) { /* never break the game */ }
};
const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode: the game still works */ } },
};
const isDaily = () => G.mode === "daily";

function init_wordle(result, csrf_token, config = {}) {
    window.csrftoken = csrf_token;
    window.result_bar = "";
    window.result = result;
    G = Object.assign({}, G, config);
    G.listKey = isDaily() ? "guess_list" : "practice_" + result.id;

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));

    // Title autocomplete (static/js/autocomplete.js): its key handler goes first, so Enter on a suggestion picks it
    const input = document.getElementById("input");
    if (input && window.Autocomplete) G.ac = Autocomplete(input, { url: config.autocompleteUrl || "/game-autocomplete/" });

    // Load save states
    let guess_list = load_game();
    play_guess(guess_list, result, "resume");

    $("#submit").click(() => submit_title(guess_list, result));
    $("#input").on("keydown", function (e) {
        if ((e.which || e.keyCode) === 13) submit_title(guess_list, result);
    });
    $("#input").on("ac:select", () => { fromList = true; });
    $("#input").on("input", () => { fromList = false; });
    watch_search();

    // Change image button action
    $(".guess").click(function () {
        let id = parseInt($(this).attr("id").replace("button", ""));
        show_image(id);
        track("select_content", { content_type: "frame", content_id: String(id + 1) });
    });

    $("#menu-stats").click(function (e) {
        e.preventDefault();
        show_stats(result);
    });
    $("#menu-info").click(function (e) {
        e.preventDefault();
        $("#info-modal").show();
        track("modal_open", { modal: "howto" });
    });
    $(".btn-close").click(() => $(".modal").hide());
    $(".modal").on("click", function (e) { if (e.target === this) $(this).hide(); });
    $(document).on("keydown", e => { if (e.key === "Escape") $(".modal").hide(); });

    // Countdown to the next daily game (00:00 UTC)
    let next = new Date();
    next.setUTCHours(24, 0, 0, 0);
    $("#clock").countdown(next).on("update.countdown", function (event) {
        $(this).html(event.strftime(""
            + '<span class="cd"><b>%H</b><small>HRS</small></span>'
            + '<span class="cd"><b>%M</b><small>MIN</small></span>'
            + '<span class="cd"><b>%S</b><small>SEC</small></span>'));
    }).on("finish.countdown", () => { if (isDaily()) location.reload(); });

    $(".btn-twitter").click(() => share("x"));
    $(".btn-whatsapp").click(() => share("whatsapp"));
    $(".btn-telegram").click(() => share("telegram"));
    $(".btn-clipboard").click(() => share("clipboard"));
    $(".btn-social").on("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); this.click(); } });
}

// Autocomplete searches, sent 1.5 s after typing stops (only the title typed and how many games matched)
function watch_search() {
    let timer = null, rendered = 0, last = "";
    $("#input").on("ac:results", e => { rendered = e.originalEvent.detail.count; });
    $("#input").on("input", function () {
        clearTimeout(timer);
        const term = this.value.trim();
        timer = setTimeout(() => {
            if (term.length < 3 || term === last) return;
            last = term;
            track("search", { search_term: term.slice(0, 60), results_found: rendered });
        }, 1500);
    });
}

// Loads the save state from localStorage. Returns the current guess list
function load_game() {
    let guess_list = [];
    if (isDaily()) {
        let saved = store.get("daily_date");
        if (saved === null && store.get("last_played") !== null) {
            // saves from before "daily_date": keep a game started today (local day), drop older ones
            const today = new Date().setHours(0, 0, 0, 0);
            if (Number(store.get("last_played")) >= today) saved = G.date;
        }
        if (saved === G.date) {
            guess_list = get_guess_list();
        } else {
            store.set("daily_date", G.date);
            set_guess_list(guess_list);
        }
        store.set("last_played", new Date().setHours(0, 0, 0, 0));
    } else {
        guess_list = get_guess_list();
    }
    if (get_stats_dict() === null) {
        store.set("stats", JSON.stringify({ "Played": 0, "Won": 0, "Current Streak": 0, "Longest Streak": 0 }));
    }
    return guess_list;
}

function set_stats_win(win) {
    let stats = get_stats_dict();
    stats["Played"] += 1;
    if (win) {
        stats["Won"] += 1;
        stats["Current Streak"] += 1;
        if (stats["Current Streak"] > stats["Longest Streak"]) stats["Longest Streak"] = stats["Current Streak"];
        if (STREAK_ACHIEVEMENTS.includes(stats["Current Streak"])) {
            track("unlock_achievement", { achievement_id: "streak_" + stats["Current Streak"] });
        }
    } else {
        stats["Current Streak"] = 0;
    }
    store.set("stats", JSON.stringify(stats));
    if (window.CLK) CLK.setUser({ daily_streak: CLK.band(stats["Current Streak"]), daily_played: CLK.band(stats["Played"]) });
}

function get_stats_dict() {
    try { return JSON.parse(store.get("stats")); } catch (e) { return null; }
}

function is_result_correct(guess, result) {
    return guess === escapeHTML(fromBinary(result["code"]));
}

// Shows the state of a guess list. how: "resume" when loading the page, "play" after a guess
function play_guess(guess_list, result, how = "play") {
    show_image(guess_list.length);
    update_guess_button(guess_list.length);
    $("#remaining").text(MAX_GUESS - guess_list.length);

    let guess = guess_list[guess_list.length - 1];
    if (guess_list && guess_list.length > 0) {
        print_guess_list(guess_list, result);
        if (is_result_correct(guess, result)) {
            show_game_data(true, result, how === "resume" ? "resume" : "end");
        } else if (guess_list.length >= MAX_GUESS) {
            show_game_data(false, result, how === "resume" ? "resume" : "end");
        }
    }
    const won = is_result_correct(guess, result);
    show_win_bar(won);
    show_hints(won || guess_list.length >= MAX_GUESS ? 0 : guess_list.length);
}

// The game's public data, fetched once (developer, platform, genre, year, cover, url)
function game_data(result) {
    if (!gameData) gameData = $.getJSON(GAMES_API + result["id"] + "/");
    return gameData;
}

// From the HINTS_FROM-th wrong guess, one more clue per miss; none once the game is over
function show_hints(misses) {
    const box = $("#hints");
    if (!box.length) return;
    const count = misses - HINTS_FROM + 1;
    if (count <= 0) { box.attr("hidden", true).empty(); return; }
    game_data(window.result).done(function (d) {
        const clues = [["Year", d.year], ["Developer", d.developer], ["Platform", d.platform], ["Genre", d.genre]]
            .filter(c => c[1] !== null && c[1] !== undefined && String(c[1]).trim() !== "");
        const shown = clues.slice(0, count);
        if (!shown.length) return;
        box.html('<h2 class="hint-title"><i class="bi bi-lightbulb-fill"></i> ' + (shown.length > 1 ? "Hints" : "Hint") + "</h2><ul>" +
            shown.map(c => "<li><b>" + c[0] + ":</b> " + escapeHTML(String(c[1])) + "</li>").join("") + "</ul>").removeAttr("hidden");
        if (box.data("shown") !== shown.length) {
            box.data("shown", shown.length);
            track("hint_view", { hint_number: shown.length, hint_type: shown[shown.length - 1][0].toLowerCase() });
        }
    });
}

// How everybody did with this game: "Today 62% of 840 players solved it, most of them on guess 2."
function show_comparison(result) {
    $.getJSON(GAMES_API + result["id"] + "/stats/").done(function (st) {
        const played = parseInt(st.played || 0, 10);
        let text = "";
        if (played > 0) {
            const solved = Math.max(0, 100 - parseInt(st["0"] || 0, 10));
            let most = 1;
            for (let i = 2; i <= MAX_GUESS; i++) if (parseInt(st[i], 10) > parseInt(st[most], 10)) most = i;
            const who = played + (played === 1 ? " player" : " players");
            const how = solved > 0 ? solved + "% of " + who + " solved it" + (solved < 100 || played > 1 ? ", most of them on guess " + most : " on guess " + most) : "nobody solved it (" + who + ")";
            text = (isDaily() ? "Today " : "When it was the daily game, ") + how + ".";
        } else if (isDaily()) {
            text = "You are among the first to finish today's game!";
        }
        $(".compare").text(text).attr("hidden", !text);
    });
}

// Links to this game's pages in the Point and Click Museum, when it has them
function show_museum_links(result) {
    $.getJSON(GAMES_API + result["id"] + "/museum/").done(function (r) {
        const links = (r && r.links) || [];
        if (!links.length) return;
        $("#museum-game").html(links.map(l => '<a class="pbtn small brass" href="' + escapeHTML(l.url) + '" target="_blank" rel="noopener" data-museum="result_' +
            l.kind + '"><i class="bi ' + (l.kind === "arcade" ? "bi-joystick" : "bi-bank2") + '"></i> ' + escapeHTML(l.label) + "</a>").join("")).removeAttr("hidden");
        $("#museum-generic").attr("hidden", true);
    });
}

function escapeHTML(string) {
    let pre = document.createElement("pre");
    pre.appendChild(document.createTextNode(string));
    return pre.innerHTML;
}

function submit_title(guess_list, result) {
    let user_title = escapeHTML($("#input").val());
    if (G.ac) G.ac.clear(); else $("#input").val("");
    if (!user_title || guess_list.length >= MAX_GUESS || is_result_correct(guess_list[guess_list.length - 1], result)) return;

    guess_list.push(user_title);
    set_guess_list(guess_list);
    const attempt = guess_list.length;
    const correct = is_result_correct(user_title, result);
    if (attempt === 1) track("level_start", { level_name: G.kind, puzzle_number: G.number || 0 });
    track("guess", { attempt: attempt, correct: correct ? "yes" : "no", from_list: fromList ? "yes" : "no" });
    fromList = false;

    play_guess(guess_list, result);

    const finished = correct || attempt >= MAX_GUESS;
    if (!finished) return;
    const score = correct ? attempt : 0;
    track("level_end", { level_name: G.kind, success: correct, attempts: attempt, puzzle_number: G.number || 0 });
    track("post_score", { score: score, level_name: G.kind });
    if (isDaily()) {
        send_hit(result, score);
        set_stats_win(correct);
    } else if (G.date) {
        try {
            const done = JSON.parse(store.get("practice_days") || "{}");
            done[G.date] = correct ? "won" : "lost";
            store.set("practice_days", JSON.stringify(done));
        } catch (e) { /* ignore */ }
    }
}

function roundup(number) {
    return parseInt(Math.ceil(number / 10.0)) - 1;
}

function removeWidthClasses(element) {
    let classes = (element.attr("class") || "").split(" ");
    for (let i = 0; i < classes.length; i++) {
        if (classes[i].startsWith("col-") || classes[i].startsWith("w-1")) element.removeClass(classes[i]);
    }
}

function show_stats(result) {
    $.getJSON(GAMES_API + result["id"] + "/stats/", function (stats) {
        for (let i = 0; i <= MAX_GUESS; i++) {
            let n = i.toString();
            $("#stats-" + n).text(stats[n]);
            removeWidthClasses($("#progress-" + n));
            $("#progress-" + n).addClass(parseInt(stats[n]) > 0 ? "col-" + roundup(stats[n]) : "w-1");
        }
        stats = get_stats_dict() || { "Played": 0, "Won": 0, "Current Streak": 0, "Longest Streak": 0 };
        $("#stats-played").text(stats["Played"]);
        $("#stats-won").text(stats["Won"]);
        $("#stats-current").text(stats["Current Streak"]);
        $("#stats-max").text(stats["Longest Streak"]);
        let percent = stats["Played"] !== 0 ? parseInt(stats["Won"]) * 100 / parseInt(stats["Played"]) : 0;
        $("#stats-winpercent").text(percent.toFixed(0) + "%");
        $("#modal-stats").show();
        track("modal_open", { modal: "stats" });
    });
}

// Shows the game. trigger: "end" (just finished), "resume" (finished earlier), "link" (View solution)
function show_game_data(is_winner, result, trigger = "link") {
    $("#result-modal-title").text(fromBinary(result["code"]));

    game_data(result).done(function (data) {
        $("#result-card-img-top").attr("src", data["cover"]
            .replace("cdn.nivoli.com/adventuregamers", "adventuregamers.com")
            .replace("adventuregamers.com/images", "adventuregamers.com/wp-content/uploads/images"))
            .attr("alt", "Cover of " + data["title"]);
        $("#result-link").attr("href", data["url"]);
        $("#card-developer").html("<strong>Developer:</strong> " + escapeHTML(data["developer"] || ""));
        $("#card-platform").html("<strong>Platform:</strong> " + escapeHTML(data["platform"] || ""));
        $("#card-genre").html("<strong>Genre:</strong> " + escapeHTML(data["genre"] || ""));
        $("#result-modal").show();
    });
    track("view_solution", { trigger: trigger });
    show_comparison(result);
    show_museum_links(result);

    show_mini_bar(is_winner);
    show_image(0);
    update_guess_button(MAX_GUESS);
    $("#remaining").hide();
    $("#searchbox").hide();

    const again = isDaily() ? "Try again tomorrow!" : "Better luck with the next one!";
    const status = is_winner ? "You won!" : is_winner === false ? again : "";
    const more = isDaily() ? "" : " · <a href='/random/' rel='nofollow'>Another random game</a>";
    $("#divguesses").html(status + " (<a href='#' id='view-solution'>View solution</a>)" + more);
    $("#view-solution").on("click", function (e) {
        e.preventDefault();
        $("#result-modal").show();
        track("modal_open", { modal: "result" });
    });
}

function send_hit(result, hit) {
    $.ajax({
        url: GAMES_API + result["id"] + "/hit/",
        type: "POST",
        beforeSend: xhr => xhr.setRequestHeader("X-CSRFToken", window.csrftoken),
        data: { "hit": hit },
    }).always(() => show_comparison(result));
}

function show_win_bar(is_winner) {
    let guess_list = get_guess_list();
    let length = is_winner ? MAX_GUESS : guess_list.length;
    let guess = guess_list.length - 1;
    for (let i = 0; i < length; i++) {
        let button = $("#result" + i);
        button.removeClass("hide");
        if (i <= guess) button.addClass("color-red").removeClass("color-grey");
        if (i === guess && is_winner) button.addClass("color-green").removeClass("color-red");
    }
}

function show_mini_bar(is_winner) {
    let guess = get_guess_list().length - 1;
    let $last = $("#br-twitter");
    if (!$last.length) return;
    $last.nextAll(".hand-grey, .hand-red, .hand-green").remove();
    const add = cls => { let $e = $("<span class='" + cls + "'>👆</span>"); $last.after($e); $last = $e; };
    window.result_bar = "";
    for (let i = 0; i < guess; i++) { add("hand-red"); window.result_bar += "🟥"; }
    if (is_winner) { add("hand-green"); window.result_bar += "🟩"; } else { add("hand-red"); window.result_bar += "🟥"; }
    for (let i = guess + 1; i < MAX_GUESS; i++) { add("hand-grey"); window.result_bar += "⬜"; }
}

function share_text(hashtag) {
    let date = new Date();
    date.setHours(0, 0, 0, 0);
    const title = (hashtag ? "#pointandclickle" : "Point & Clickle") + (G.number ? " #" + G.number : "");
    return title + " - " + date.toDateString() + "\n👆 " + window.result_bar + "\n 🔗 https://pointandclickle.com";
}

function is_mobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function share(method) {
    const text = share_text(method === "x");
    if (method === "x") {
        window.open("https://twitter.com/intent/tweet?text=" + encodeURIComponent(text));
    } else if (method === "whatsapp") {
        window.open((is_mobile() ? "whatsapp://send?text=" : "https://web.whatsapp.com/send?text=") + encodeURIComponent(text));
    } else if (method === "telegram") {
        window.open("https://telegram.me/share/url?url=" + encodeURIComponent("https://pointandclickle.com") + "&text=" + encodeURIComponent(text));
    } else {
        navigator.clipboard.writeText(text);
        new bootstrap.Toast($("#liveToast")).show();
    }
    track("share", { method: method, content_type: "result", item_id: G.kind + (G.number ? "-" + G.number : "") });
}

// Shows an image guess
function show_image(num_guess) {
    num_guess = Math.min(num_guess, MAX_GUESS - 1);
    for (let i = 0; i < MAX_GUESS; i++) {
        $("#img" + i).toggleClass("hide", i !== num_guess);
        $("#button" + i).toggleClass("current", i === num_guess).attr("aria-pressed", i === num_guess);
    }
    $("#frame-n").text(num_guess + 1);
}

// Shows the buttons of the screenshots already unlocked
function update_guess_button(num_guess) {
    for (let i = 0; i < MAX_GUESS; i++) $("#button" + i).toggleClass("hide", i > num_guess);
}

function get_guess_list() {
    try { return JSON.parse(store.get(G.listKey)) || []; } catch (e) { return []; }
}

function set_guess_list(list) {
    if (list) store.set(G.listKey, JSON.stringify(list));
}

function print_guess_list(guess_list, result) {
    let ul = $("#guesses-list");
    ul.empty();
    for (let i = 0; i < guess_list.length; i++) {
        const icon = is_result_correct(guess_list[i], result) ? '<i class="bi bi-check"></i>' : '<i class="bi bi-x"></i>';
        ul.append('<li class="list-group-item">' + icon + guess_list[i] + "</li>");
    }
}

function fromBinary(str) {
    return decodeURIComponent(atob(str).split("").map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2)).join(""));
}
