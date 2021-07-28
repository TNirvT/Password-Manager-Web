const btnCopy=document.getElementById("btn-copyPass");
if (btnCopy.value) {
    btnCopy.addEventListener("click", () => {
    navigator.clipboard.writeText(btnCopy.value);
    console.log("copy btn clicked")
    })
};

const btnGen=document.getElementById("btn-gen-new");
function btnPost(){
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/content", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        id_for_pw: btnGen.value
    }));
    // $.post( "/content", {
    //     javascript_data: 103
    // });
};
// btnGen.addEventListener("click", function (){
//     btnPost();
// })

const anchorDel=document.getElementById("anchor-del");
anchorDel.addEventListener("click", () => {
    document.getElementById('form-del').submit()
})