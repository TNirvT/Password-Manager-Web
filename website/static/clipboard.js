const btnCopy=document.getElementById("btn-copyPass")
if (btnCopy.value) {
    btnCopy.addEventListener("click", function (){
    navigator.clipboard.writeText(btnCopy.value)    
    })
}