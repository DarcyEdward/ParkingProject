document.getElementById("loginForm").addEventListener("submit", async function(e) {
    e.preventDefault(); // 🚫 stop page change


    //create the table for the backend.
    const formData = new FormData();
    formData.append("email", document.getElementById("email").value);
    formData.append("password", document.getElementById("password").value);


    //Sends the data to the backend
    const res = await fetch("/login", {
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
    window.location.href = "/";
    }, 500);


});

