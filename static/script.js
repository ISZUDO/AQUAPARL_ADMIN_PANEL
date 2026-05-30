let selectedId = null;
let selectedEl = null;
let activeTimers = {}; // har bir locker uchun interval saqlash

function selectLocker(el){
    selectedEl = el;
    selectedId = el.dataset.id;
    document.getElementById("modal").style.display = "flex";
}

function closeModal(){
    document.getElementById("modal").style.display = "none";
}

function setNormal(){
    fetch("/set_normal", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({id: selectedId})
    })
    .then(res => res.json())
    .then(data => {
        selectedEl.className = "locker busy";
        startTimer(selectedEl, 1 * 60, selectedId);
        closeModal();
    });
}

function setVIP(){
    fetch("/set_vip", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({id: selectedId})
    })
    .then(res => res.json())
    .then(data => {
        // Agar timer bo'lsa to'xtat
        if(activeTimers[selectedId]){
            clearInterval(activeTimers[selectedId]);
            delete activeTimers[selectedId];
        }
        selectedEl.className = "locker vip";
        selectedEl.querySelector(".time").innerText = "VIP";
        closeModal();
    });
}

function freeLocker(){
    fetch("/free", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({id: selectedId})
    })
    .then(res => res.json())
    .then(data => {
        // Agar timer bo'lsa to'xtat
        if(activeTimers[selectedId]){
            clearInterval(activeTimers[selectedId]);
            delete activeTimers[selectedId];
        }
        selectedEl.className = "locker empty";
        selectedEl.querySelector(".time").innerText = "Bo'sh";
        closeModal();
    });
}

function startTimer(el, seconds, id){
    // Agar avvalgi timer bo'lsa to'xtat
    if(activeTimers[id]){
        clearInterval(activeTimers[id]);
    }

    let time = seconds;

    activeTimers[id] = setInterval(() => {
        let h = Math.floor(time / 3600);
        let m = Math.floor((time % 3600) / 60);
        let s = time % 60;

        el.querySelector(".time").innerText =
            `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;

        time--;

        if(time < 0){
            clearInterval(activeTimers[id]);
            delete activeTimers[id];
            el.className = "locker expired";
            el.querySelector(".time").innerText = "TUGADI";

            let audio = new Audio("/static/alarm.mp3");
            audio.play();
        }
    }, 1000);
}
