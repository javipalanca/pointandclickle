const MAX_GUESS = 6; // Define the maximum number of guesses

function init_wordle(result) {

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

    return guess_list;
}

function is_result_correct(guess, result) {
    return guess === fromBinary(result);
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

function escapeHTML( string )
{
    var pre = document.createElement('pre');
    var text = document.createTextNode( string );
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
}


// Shows the game
function show_game_data(is_winner, result) {
    // Show title
    $(".modal-title").text(fromBinary(result));

    // Show cover
    $(".modal").show();

    // Show all images
    show_image(0);

    // Show all buttons
    update_guess_button(MAX_GUESS);

    // Hide remaining guesses
    $("#remaining").hide();

    // Hide submit button
    //$("#submit").hide();
    $("#searchbox").hide();

    // Show result
    if (is_winner) {
        $("#divguesses").html("You won! (<a href='#' onclick='$(\".modal\").show();'>View solution)</a>");
    } else {
        $("#divguesses").text("Try again tomorrow!");
    }
}

function show_win_bar(is_winner) {
    let guess_list = get_guess_list();
    let length = guess_list.length;
    if(is_winner) {
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

