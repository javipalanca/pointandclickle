const MAX_GUESS = 6; // Define the maximum number of guesses

function init_wordle(result) {

    // Load save states
    let guess_list = load_game();
    play_guess(guess_list, result);

    // User submit guess action
    $("#submit").click(function () {
        // update the guess list
        let user_title = $("#input").val();
        $("#input").val("");
        if (user_title && guess_list.length < MAX_GUESS) {
            guess_list.push(user_title);
            set_guess_list(guess_list);
        }
        // Check de result
        play_guess(guess_list, result);
    });

    // Change image button action
    $(".guess").click(function () {
        let id = parseInt($(this).attr("id").replace("button", ""));
        show_image(id);
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


// Checks the last played guess
function play_guess(guess_list, result) {
    // show image
    show_image(guess_list.length);

    // Update game buttons
    update_guess_button(guess_list.length);

    // Update number guesses
    $("#remaining").text(MAX_GUESS - guess_list.length);

    // Update guess list
    if (guess_list && guess_list.length > 0) {
        // Print guess list
        print_guess_list(guess_list);

        // Get current guess
        let guess = guess_list[guess_list.length - 1];
        console.log("Playing " + guess + " ...")

        // Check if the result is correct
        if (guess === fromBinary(result)) {
            show_game_data(true, result);
        } else {
            if (guess_list.length < MAX_GUESS) {
                console.log("Try again...");
            } else {
                show_game_data(false, result);
            }
        }
    }
}


// Shows the game
function show_game_data(is_winner, result) {
    // Show title
    $("#cover h1").text(fromBinary(result));

    // Show cover
    $("#cover").show();

    // Hide image
    show_image(-1);

    // Hide buttons
    update_guess_button(-1);

    // Hide remaining guesses
    $("#remaining").hide();

    // Hide submit button
    $("#submit").hide();
    $("#input").hide();

    // Show result
    if (is_winner) {
        $("#divguesses").text("You won!");
    } else {
        $("#divguesses").text("Try again tomorrow!");
    }
    show_win_bar(result);
}

function show_win_bar(result) {
    for (let i = 0; i < 6; i++) {
        let button = $("#result" + i);
        button.removeClass("hide");
        let guess_list = get_guess_list();
        let guess = guess_list.length - 1;
        if (i < guess) {
            button.addClass("btn-danger");
            button.removeClass("btn-secondary");
        } else if (i === guess && guess_list[i] === fromBinary(result)) {
            button.addClass("btn-success");
            button.removeClass("btn-secondary");
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

function print_guess_list(guess_list) {
    let ul_guesses = $("#guesses-list");
    ul_guesses.empty();
    for (let i = 0; i < guess_list.length; i++) {
        ul_guesses.append("<li>" + guess_list[i] + "</li>");
    }
}

function fromBinary(str) {
    // Going backwards: from bytestream, to percent-encoding, to original string.
    return decodeURIComponent(atob(str).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}

