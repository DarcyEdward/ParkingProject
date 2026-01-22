document.getElementById("registerForm").addEventListener("submit", async function(e) {
    e.preventDefault(); // 🚫 stop page change

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const password2 = document.getElementById("password2").value;


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

    const data = await res.json();


    if (!data.success) {
        showToast(data.message, "error");
        return;
    }

    //sends the user to the login page.
    showToast(data.message, "success");

    setTimeout(() => {
    window.location.href = "/static/login.html";
    }, 500);


});

