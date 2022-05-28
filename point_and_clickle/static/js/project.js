function init_wordle(result) {
    today = new Date().setHours(0, 0, 0, 0);

    let guess;

    if (localStorage.getItem("last_played") === null || localStorage.getItem("last_played") < today) {
        console.log("Initializing storage");
        localStorage.setItem("last_played", today);
        localStorage.setItem("current_guess", "0");
        localStorage.setItem("guess_list", "[]");
        guess = 0;

    } else {
        console.log("Storage already initialized");
        guess = parseInt(localStorage.getItem("current_guess"));
    }
    update_guesses(guess);
    if (guess>=6  || check_win_condition(result)) {
        showResult(result);
    }

    $(".guess").click(function () {
        let id = parseInt($(this).attr("id").replace("button", ""));
        for (let i = 0; i < 6; i++) {
            if (i === id) {
                $("#img" + i).removeClass("hide");
            } else {
                $("#img" + i).addClass("hide");
            }
        }
    });

    $("#submit").click(function () {
        let title = $("#input").val();
        if (title === fromBinary(result)) {
            console.log("Correct!");
            guess = 6;
            update_guesses(guess);
            showResult(result);
        } else {
            console.log("Incorrect!");
            guess++;
            update_guesses(guess);
            if (guess >= 6) {
                console.log("Game over!");
                showResult(result);
            }
        }
        $("#input").val('');

    });
}

function fromBinary(str) {
    // Going backwards: from bytestream, to percent-encoding, to original string.
    return decodeURIComponent(atob(str).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}

function update_guesses(guess) {
    for (let i = 0; i < 6; i++) {
        if (i <= guess) {
            $("#button" + i).removeClass("hide");
        } else {
            $("#button" + i).addClass("hide");
        }
        if (i === guess) {
            $("#img" + i).removeClass("hide");
        } else {
            $("#img" + i).addClass("hide");
        }
        if (guess >= 6) {
            $("#img0").removeClass("hide");
        }
    }
    $("#remaining").text(6 - guess);

    localStorage.setItem("current_guess", guess.toString());

    update_guess_list();
}


function showResult(result) {
    $("#submit").hide();
    $("#input").hide();
    console.log("Titulo: " + fromBinary(result));
    $("#cover h1").text(fromBinary(result));
    $("#cover").show();

    if (!check_win_condition(result)) {
        $("#divguesses").text("Try again tomorrow!");
    }
    else {
        $("#divguesses").text("You won!");
    }
}

function check_win_condition(result) {
    let list = localStorage.getItem("guess_list");
    if (list !== "[]" && list !== undefined) {
        list = JSON.parse(list);
        return list[list.length - 1] === fromBinary(result);
    }
    return false;
}

function update_guess_list() {
    let title = $("#input").val();
    let list = localStorage.getItem("guess_list");
    if (title) {
        if (list !== "[]" && list !== undefined) {
            list = JSON.parse(list);
            list.push(title.toString());
            list = JSON.stringify(list);
        } else {
            list = '["' + title.toString() + '"]';
        }
        localStorage.setItem("guess_list", list);
    }
    $("#guesses-list").empty();
    if (list !== "[]" && list !== undefined) {
        list = JSON.parse(list);
        for (let i = 0; i < list.length; i++) {
            $("#guesses-list").append("<li>" + list[i] + "</li>");
        }
    }
}
