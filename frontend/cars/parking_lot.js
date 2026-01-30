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
  }else if(type === "day"){
    type_num = (parkingRates.daily * amount)+ 0.25;
  }else {
    type_num = (parkingRates.monthly * amount) + 0.25;
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
  console.log((parkingRates.hourly))
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



