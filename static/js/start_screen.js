async function getLocation(){
    const location = await axios.get("/location/get")
    select = document.getElementById("locations")

    for(var i=0;i<location.length;i++)
    {
        var add = document.createElement('option')
        add.value = location[i]
        add.innerHTML = location[i]
        select.appendChild(add)
    }
}

getLocation();