function checkEmail(){
    var email = document.getElementById("email").value
    var confirmEmail = document.getElementById("confirmEmail").value
    if(confirmEmail!==email)
        document.getElementById("confirmEmail").style.color = "red"
    else
        document.getElementById("confirmEmail").style.color = "black"
}