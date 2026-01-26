//Logout button!!!
document.getElementById("logoutButton").addEventListener("click", async () => {

    const res = await fetch("/logout", {
        method: "POST",
        credentials: "include"
    });

    //user has been logged out!
    const data = await res.json();
    showToast(data.message, "success");

    setTimeout(() => {
    window.location.href = "/";
    }, 200);

})

document.getElementById("back").addEventListener("click", async () => {
    window.location.href = "/";
})