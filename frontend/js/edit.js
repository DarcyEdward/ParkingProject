const carEditForm = document.getElementById("carEditForm");

if (carEditForm){
    carEditForm.addEventListener("submit", async function(e) {
        e.preventDefault(); // 🚫 stop page change

        action = e.submitter.id;

        let res;
        const formData = new FormData();
        car_id = new URLSearchParams(window.location.search).get("id");
        formData.append("car_id", car_id);

        //create the table for the backend.
        if (action === "saveCar") {
            console.log("Save car is submitted!")
            formData.append("make", document.getElementById("make").value);
            formData.append("model", document.getElementById("model").value);
            formData.append("year", document.getElementById("year").value);
            formData.append("plate", document.getElementById("plate").value);
            formData.append("color", document.getElementById("color").value);

            //Sends the data to the backend
            res = await fetch("/updateCar", {
                method: "POST",
                body: formData
            });
        }


        else if (action === "deleteCar"){
            res = await fetch("/deleteCar", {
                method: "POST",
                body: formData
            });
        }

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
}


const add_btn = document.getElementById("editCars");

if(add_btn){
    add_btn.addEventListener("click", async () => {

        let res = await fetch("/addCar", {
            method: "POST"
        });
        const data = await res.json();

        if (!data.success) {
            showToast(data.message, "error");
            return;
        }

        //sends the user to the login page
        showToast(data.message, "success");
        window.location.href = "/";

    });
}


