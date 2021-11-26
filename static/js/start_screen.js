function checkEmail(){
    var email = document.getElementById("email").value
    var confirmEmail = document.getElementById("confirmEmail").value
    if(confirmEmail!==email)
        document.getElementById("confirmEmail").style.color = "red"
    else
        document.getElementById("confirmEmail").style.color = "black"
}

axios.post('/testing', {
    bookings: {
        1: {
            times: [[1, 2]],
            studyTableName: "table 1"
        }
    }
  })
  .then(function (response) {
    console.log(response);
  })