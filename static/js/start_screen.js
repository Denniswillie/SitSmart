function checkEmail(){
    var email = document.getElementById("email").value
    var confirmEmail = document.getElementById("confirmEmail").value
    if(confirmEmail!==email)
        document.getElementById("confirmEmail").style.color = "red"
    else
        document.getElementById("confirmEmail").style.color = "black"
}

function handleSubmit() {
    var email = document.getElementById("email").value
    var confirmEmail = document.getElementById("confirmEmail").value
    var form = document.getElementById("startScreenForm")
    if (email === confirmEmail) {
        form.submit();
    } else {
        alert("Confirmation email must be equal to the email.")
    }
}