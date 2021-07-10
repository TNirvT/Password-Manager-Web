const btnCopy=document.getElementById("btn-copyPass");
if (btnCopy.value) {
    btnCopy.addEventListener("click", function (){
    navigator.clipboard.writeText(btnCopy.value)    
    })
};

const btnGen=document.getElementById("btn-gen-new");
btnGen.addEventListener("click", function (){
    $.post("/content", {
        id_for_pw: btnGen.value
    })
});