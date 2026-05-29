
// MODAL OPEN
function openModal(place, gender) {
    document.getElementById("placeInput").value = place;
    document.getElementById("genderInput").value = gender;
    document.getElementById("modal").style.display = "flex";
}

// MODAL CLOSE
function closeModal() {
    document.getElementById("modal").style.display = "none";
}


// 🔄 LIVE STATUS UPDATE (FAQAT RANG)
setInterval(() => {

    fetch("/status")
        .then(res => res.json())
        .then(data => {

            document.querySelectorAll(".place").forEach(el => {

                let number = el.innerText.trim();
                let status = data[number];

                // eski ranglarni tozalash
                el.classList.remove("free", "occupied", "expired");

                // faqat 2 holat:
                if (status === "free") {
                    el.classList.add("free");
                } else {
                    el.classList.add("occupied");
                }

            });

        });

}, 3000);