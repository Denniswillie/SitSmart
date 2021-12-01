async function googleLogin()
{
    let location=document.getElementById("locations").value;
    if(location ==="null")
    {
        alert("Please select a location first");
    }
    else
    {
        let formdata = new FormData();
         formdata.append('location_id',location)
         await axios({
        method: "POST",
        url: "/register",
        data: formdata,
        headers: { "Content-Type": "multipart/form-data" },
        })
        .then(res=>res.data)
        .catch(err=>console.log(err))
        .then(res=>{
            if(res.stored)
            {
                window.location.href = "/login"
            }
        })
    }
}