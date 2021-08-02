const axios = require('axios');

// const navItemUnlocked = document.getElementsByClassName("nav-item-unlocked");
// const navLength = navItemUnlocked.length
// if (window.location.pathname !== "/"){
//     for (let i=0; i < navLength; i++){
//         navItemUnlocked.item(0).remove()
//     }
// };
const navItemUnlocked = document.querySelectorAll(".nav-item-unlocked");
if (window.location.pathname === "/"){
    navItemUnlocked.forEach( (el) => {
        el.remove();
    })
};

const btnMasterPw = document.getElementById("btn-master-pw");
const inputMasterPw = document.getElementById("master_pw");
// inputMasterPw.addEventListener("input", pwLengthChk);

function pwLengthChk (){
    let xhr = new XMLHttpRequest();
}

const btnCopy = document.getElementById("btn-copyPass");
if (window.location.pathname.indexOf("/content/") > -1 && btnCopy.value){
    btnCopy.addEventListener("click", () => {
    navigator.clipboard.writeText(btnCopy.value);
    console.log("copy btn clicked")
    })
};

// const btnGen = document.getElementById("btn-gen-new");
// function btnPost(){
//     const xhr = new XMLHttpRequest();
//     xhr.open("POST", "/content", true);
//     xhr.setRequestHeader('Content-Type', 'application/json');
//     xhr.send(JSON.stringify({
//         id_for_pw: btnGen.value
//     }));
//     $.post( "/content", {
//         javascript_data: 103
//     });
// };
// btnGen.addEventListener("click", function (){
//     btnPost();
// })

const anchorDel = document.getElementById("anchor-del");
if (window.location.pathname.indexOf("/content/") > -1){
    anchorDel.addEventListener("click", () => {
        document.getElementById('form-del').submit()
    });
}