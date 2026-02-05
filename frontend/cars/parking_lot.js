const hourly = document.getElementById("hourly-question");
const daily = document.getElementById("daily-question");
const monthly = document.getElementById("monthly-question");
const passType = document.getElementById("pass-type");

passType.addEventListener("change", () => {
    // hide both first
  hourly.hidden = true;
  daily.hidden = true;
  monthly.hidden = true;

  if (passType.value === "hour") {
    hourly.hidden = false;
  }

  if (passType.value === "daily") {
    daily.hidden = false;
  }

  if (passType.value === "month") {
    monthly.hidden = false;
  }
});

function updateReceipt(type, amount){
  let type_num;
  if(type === "hr"){
    type_num = (parkingRates.hourly * amount) + 0.25;
    document.getElementById("parkeduntil").textContent = new Date(new Date().getTime() + amount * 60 * 60 * 1000).toLocaleString();
  }else if(type === "day"){
    type_num = (parkingRates.daily * amount)+ 0.25;
    document.getElementById("parkeduntil").textContent = new Date(new Date().getTime() + amount * 24 * 60 * 60 * 1000).toLocaleString().split(" ")[0] + " 3:00 PM";
  }else {
    type_num = (parkingRates.monthly * amount) + 0.25;
    document.getElementById("parkeduntil").textContent = new Date(new Date().getTime() + amount * 24 * 30 * 60 * 60 * 1000).toLocaleString().split(",")[0];
  }

  document.getElementById("rate").textContent = "Rate: $" + ((type_num - .25) / amount).toFixed(2) + "/" + type + " * " + amount + type + "(s)";
  document.getElementById("subtotal").textContent = "SUBTOTAL: $" + type_num.toFixed(2);

  document.getElementById("taxes").textContent = "Taxes: $" + (type_num * 0.04).toFixed(2);
  document.getElementById("total").textContent = "TOTAL: $" + (type_num * 1.04).toFixed(2);

}

const untilInput = document.getElementById("until-day");

untilInput.min = new Date().toISOString().split("T")[0];


//Hours section

document.getElementById("hours").addEventListener("change", () => {
  if(hours.value < 0.5){
    hours.value = .5;
  }
  updateReceipt("hr",hours.value);
});


//Days section

document.getElementById("until-day").addEventListener("change", () => {
  daysInput = document.getElementById("until-day").value;
  updateReceipt("day", (Math.ceil((new Date(daysInput) - Date.now()) / 86400000) + 1));
});

//Months section

document.getElementById("until-month").addEventListener("change", () => {
  daysInput = document.getElementById("until-month").value;
  updateReceipt("month", daysInput);
});













document.getElementById("parkCar").addEventListener("submit", async function(e) {
  e.preventDefault(); // 🚫 stop page change
  amountDays = Math.ceil((new Date(document.getElementById("until-day")?.value || 0) - Date.now()) / 86400000) + 1;
  if(amountDays < 0) {
    amountDays = 0;
  }

  const formData = new FormData();
  formData.append("lot_id", parkingRates.id)
  formData.append("car", document.getElementById("which-car").value);
  formData.append("pass_type", passType.value);
  formData.append("hours", document.getElementById("hours")?.value || 0);
  formData.append("days", amountDays);
  formData.append("months", document.getElementById("until-month")?.value || 0);



    //Sends the data to the backend
    const res = await fetch("/pay", {
        method: "POST",
        body: formData,
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
    }, 1000);


});












