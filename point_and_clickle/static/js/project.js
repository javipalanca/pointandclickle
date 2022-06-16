const MAX_GUESS = 6; // Define the maximum number of guesses
const GAMES_API = '/api/v1/game/';

function init_wordle(result, csrf_token) {

    window.csrftoken = csrf_token;

    // Load save states
    let guess_list = load_game();
    play_guess(guess_list, result);

    // User submit guess action
    $("#submit").click(function () {
        submit_title(guess_list, result);
    });

    $("#input").on("keydown", function (e) {
        let keycode = e.which || e.keyCode;
        if (keycode === 13) // enter key code
            submit_title(guess_list, result);
    });

    // Change image button action
    $(".guess").click(function () {
        let id = parseInt($(this).attr("id").replace("button", ""));
        show_image(id);
    });

    // Show stats
    $("#menu-stats").click(function () {
        show_stats(result);
    });
    // Show info
    $("#menu-info").click(function () {
        $("#info-modal").show();
    });

    // Close modal window
    $(".btn-close").click(function () {
        $(".modal").hide();
    });
}

// Loads the save state from localStorage. Returns the current guess list
function load_game() {
    let today = new Date().setHours(0, 0, 0, 0); // Today timestap

    let guess_list = [];

    if (localStorage.getItem("last_played") === null || localStorage.getItem("last_played") < today) {
        // New game
        console.log("Creating new game...");
        localStorage.setItem("last_played", today);
        set_guess_list(guess_list);
    } else {
        // Restore saved game
        console.log("Loading saved game...");
        guess_list = get_guess_list();
    }
    if (get_stats_dict() === null) {
        localStorage.setItem("stats", JSON.stringify({"Played": 0, "Won": 0, "Current Streak": 0, "Longest Streak": 0}));
    }

    return guess_list;
}

function set_stats_win(win) {
    let stats = get_stats_dict();
    stats['Played'] += 1;
    if (win) {
        stats['Won'] += 1;
        stats['Current Streak'] += 1;
        if (stats['Current Streak'] > stats['Longest Streak']) {
            stats['Longest Streak'] = stats['Current Streak'];
        }
    }
    else {
        stats['Current Streak'] = 0;
    }
    localStorage.setItem("stats", JSON.stringify(stats));
}

function get_stats_dict() {
    return JSON.parse(localStorage.getItem("stats"));
}

function is_result_correct(guess, result) {
    return guess === fromBinary(result['code']);
}

// Checks the last played guess
function play_guess(guess_list, result) {
    // show image
    show_image(guess_list.length);

    // Update game buttons
    update_guess_button(guess_list.length);

    // Update number guesses
    $("#remaining").text(MAX_GUESS - guess_list.length);

    // Update guess list
    let guess = guess_list[guess_list.length - 1];
    if (guess_list && guess_list.length > 0) {
        // Print guess list
        print_guess_list(guess_list, result);

        // Get current guess
        console.log("Playing " + guess + " ...")

        // Check if the result is correct
        if (is_result_correct(guess, result)) {
            show_game_data(true, result);
        } else {
            if (guess_list.length < MAX_GUESS) {
                console.log("Try again...");
            } else {
                show_game_data(false, result);
            }
        }
    }
    show_win_bar(is_result_correct(guess, result));
}

function escapeHTML(string) {
    let pre = document.createElement('pre');
    let text = document.createTextNode(string);
    pre.appendChild(text);
    return pre.innerHTML;
}

function submit_title(guess_list, result) {
    // update the guess list
    let user_title = escapeHTML($("#input").val());
    $("#input").val("");
    if (user_title && guess_list.length < MAX_GUESS) {
        guess_list.push(user_title);
        set_guess_list(guess_list);
    }
    // Check de result
    play_guess(guess_list, result);
    // Check if the result is correct
    if (is_result_correct(user_title, result)) {
        send_hit(result, guess_list.length);
        set_stats_win(true);
    } else {
        if (guess_list.length >= MAX_GUESS) {
            send_hit(result, 0);
            set_stats_win(false);
        }
    }
}

function roundup(number) {
    return parseInt(Math.ceil(number / 10.0)) - 1;
}

function removeWidthClasses(element) {
    let classes = element.attr("class").split(" ");
    for (let i = 0; i < classes.length; i++) {
        if (classes[i].startsWith("col-") || classes[i].startsWith("w-1")) {
            element.removeClass(classes[i]);
        }
    }
}

function show_stats(result) {
    //Get stats from API
    $.getJSON(GAMES_API + result['id'] + "/stats/", function (stats) {
        let col;
        for (let i=0; i<=MAX_GUESS; i++) {
            let n = i.toString();
            $("#stats-"+n).text(stats[n]);
            col = parseInt(stats[n]) > 0 ? "col-" + roundup(stats[n]) : "w-1";
            removeWidthClasses($("#progress-"+n));
            $("#progress-"+n).addClass(col);
        }


        stats = get_stats_dict();
        $("#stats-played").text(stats['Played']);
        $("#stats-won").text(stats['Won']);
        $("#stats-current").text(stats['Current Streak']);
        $("#stats-max").text(stats['Longest Streak']);
        console.log(stats);
        let percent = stats['Played']!==0?parseInt(stats['Won'])*100/parseInt(stats['Played']):0;
        $("#stats-winpercent").text(percent.toFixed(0)  + "%");

        $("#modal-stats").show();
    });
}


// Shows the game
function show_game_data(is_winner, result) {
    // Show title
    $("#result-modal-title").text(fromBinary(result['code']));

    $.getJSON(GAMES_API + result['id'])
        .done(function (data) {
            // Show game data
            $("#result-card-img-top").attr("src", data['cover']);
            $("#result-card-title").text(data['title']);
            $("#result-link").attr("href", data['url']);
            $("#card-developer").html("<strong>Developer:</strong> " + data['developer']);
            $("#card-platform").html("<strong>Platform:</strong> " + data['platform']);
            $("#card-genre").html("<strong>Genre:</strong> " + data['genre']);

            $("#result-modal").show();
        });


    // Show all images
    show_image(0);

    // Show all buttons
    update_guess_button(MAX_GUESS);

    // Hide remaining guesses
    $("#remaining").hide();

    // Hide searchbox
    $("#searchbox").hide();

    // Show result
    if (is_winner) {
        $("#divguesses").html("You won! (<a href='#' onclick='$(\"#result-modal\").show();'>View solution)</a>");
    } else {
        $("#divguesses").html("Try again tomorrow! (<a href='#' onclick='$(\"#result-modal\").show();'>View solution)</a>");
    }
}

function send_hit(result, hit) {
    $.ajax({
        url: GAMES_API + result['id'] + "/hit/",
        type: "POST",
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", window.csrftoken);
        },
        data: {
            "hit": hit
        },
        success: function (data) {
            console.log("Hit " + hit + " sent!");
        },
        error: function (data) {
            console.log("Error sending hit!");
        }
    });
}

function show_win_bar(is_winner) {
    let guess_list = get_guess_list();
    let length = guess_list.length;
    if (is_winner) {
        length = MAX_GUESS;
    }
    for (let i = 0; i <= length; i++) {

        let button = $("#result" + i);
        button.removeClass("hide");
        let guess = guess_list.length - 1;
        if (i <= guess) {
            button.addClass("color-red");
            button.removeClass("color-grey");
        }
        if (i === guess && is_winner) {
            button.addClass("color-green");
            button.removeClass("color-red");
        }
    }
}

// Shows an image guess
function show_image(num_guess) {
    for (let i = 0; i < MAX_GUESS; i++) {
        if (i === num_guess) {
            $("#img" + i).removeClass("hide");
        } else {
            $("#img" + i).addClass("hide");
        }
    }
}

// Shows the button number...
function update_guess_button(num_guess) {
    for (let i = 0; i < MAX_GUESS; i++) {
        if (i <= num_guess) {
            $("#button" + i).removeClass("hide");
        } else {
            $("#button" + i).addClass("hide");
        }
    }
}

// Gets the localStorage guess list as an object
function get_guess_list() {
    let list = [];
    let local = localStorage.getItem("guess_list");
    if (local) {
        list = JSON.parse(local);
    }
    return list;
}

// Sets the list in localStorage as string
function set_guess_list(list) {
    if (list) {
        let local = JSON.stringify(list);
        localStorage.setItem("guess_list", local);
    }
}

function print_guess_list(guess_list, result) {
    let ul_guesses = $("#guesses-list");
    ul_guesses.empty();
    let icon;
    for (let i = 0; i < guess_list.length; i++) {
        if (is_result_correct(guess_list[i], result)) {
            icon = "<i class=\"bi bi-check\"></i>";
        } else {
            icon = "<i class=\"bi bi-x\"></i>";
        }
        ul_guesses.append("<li class=\"list-group-item\">" + icon + guess_list[i] + "</li>");
    }
}

function fromBinary(str) {
    // Going backwards: from bytestream, to percent-encoding, to original string.
    return decodeURIComponent(atob(str).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}

