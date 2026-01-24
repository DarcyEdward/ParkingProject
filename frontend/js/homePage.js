const loggedOut = document.getElementById("logged-out");
const loggedIn = document.getElementById("logged-in");

fetch("/me", { credentials: "include" })
    .then(res => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
    })
    .then(data => {
        console.log("Logged in:", data.user_id);

        loggedOut.hidden = true;
        loggedIn.hidden = false;
    })
    .catch(() => {
        console.log("Not logged in.");
        loggedOut.hidden = false;
        loggedIn.hidden = true;
    });
