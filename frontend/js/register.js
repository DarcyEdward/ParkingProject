document.getElementById("registerForm").addEventListener("submit", async function(e) {
    e.preventDefault(); // 🚫 stop page change

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const password2 = document.getElementById("password2").value;
    const errorMsg = document.getElementById("errorMsg");
    errorMsg.style = "color: #b12929;";

    if(username.length < 4 || password.length < 4) {
        errorMsg.textContent = "Both your username and password need to be at least 5 characters.";
        return;
    }

    if (password !== password2) {
        errorMsg.textContent = "Passwords do not match";
        return;
    }

    //create the table for the backend.
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    formData.append("password2", password2);

    //Sends the data to the backend
    const res = await fetch("/register", {
        method: "POST",
        body: formData
    });

    //If the response is not good this will happen...

    if (res.status != 200) {
        const data = await res.json();
        errorMsg.textContent = data.detail;
        return;
    }

    errorMsg.style.color = "green";
    errorMsg.textContent = "Registered successfully!";

    //sends the user to the login page.
    setTimeout(() => {
    window.location.href = "/static/login.html";
    }, 500);

});

