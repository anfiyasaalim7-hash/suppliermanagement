// ================= API URL =================
const API = "http://localhost:8000";

// ================= STEP NAVIGATION =================
let steps = document.querySelectorAll(".step");

function nextStep(i){
    steps.forEach(step => step.classList.remove("active"));
    steps[i].classList.add("active");
}

function back(){
    steps.forEach(step => step.classList.remove("active"));
    steps[0].classList.add("active");
}


// ================= CREATE VENDOR =================
function createVendor(){

    const shop_name = document.getElementById("shop_name").value;
    const owner = document.getElementById("owner").value;
    const contact = document.getElementById("contact").value;

    fetch(API + "/vendor/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `shop_name=${shop_name}&owner=${owner}&contact=${contact}`
    })
    .then(res => res.json())
    .then(data => {
        alert("✅ Vendor Created Successfully");
        loadVendors();
        back();
    })
    .catch(err => {
        alert("❌ Error creating vendor");
        console.error(err);
    });
}


// ================= CREATE INVOICE =================
function createInvoice(){

    const vendor_id = document.getElementById("vendor_id").value;
    const amount = document.getElementById("amount").value;

    fetch(API + "/invoice/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `vendor_id=${vendor_id}&amount=${amount}`
    })
    .then(res => res.json())
    .then(data => {
        alert("🧾 Invoice Created");
        back();
    })
    .catch(err => {
        alert("❌ Error creating invoice");
        console.error(err);
    });
}


// ================= PAY INVOICE =================
function payInvoice(){

    const invoice_id = document.getElementById("invoice_id").value;

    fetch(API + "/payment/pay", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `invoice_id=${invoice_id}`
    })
    .then(res => res.json())
    .then(data => {
        alert("💰 Payment Successful");
        loadVendors();
        back();
    })
    .catch(err => {
        alert("❌ Payment Failed");
        console.error(err);
    });
}


// ================= LOAD VENDORS =================
function loadVendors(){

    fetch(API + "/vendors")
    .then(res => res.json())
    .then(data => {

        const list = document.getElementById("vendorList");
        list.innerHTML = "";

        data.forEach(vendor => {

            list.innerHTML += `
                <li>
                    <strong>${vendor.shop_name}</strong><br>
                    Owner: ${vendor.owner}<br>
                    Contact: ${vendor.contact}<br>
                    Score: ${vendor.score}%
                </li>
            `;
        });

    })
    .catch(err => {
        console.error("Error loading vendors:", err);
    });
}


// ================= AUTO LOAD ON START =================
window.onload = loadVendors;
