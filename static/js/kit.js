function formatHr(hour){
    hour = hour<10?'0'+hour:hour;
    return hour;
}

function formatDate(today)
{
    var mon = today.getMonth();
    var day = today.getDate();
    if(mon<10)
        mon = '0'+mon;
    if(day<10)
        day = '0'+day;

    var res =today.getFullYear()+"-"+mon+"-"+day;
    return res;
}

function formatTime(today,second)
{
    var hr = today.getHours();
    var min = today.getMinutes();
    var sec = today.getSeconds();
    if(hr<10)
        hr = '0'+hr;
    if(min<10)
        min = '0'+min;
    if(sec<10)
        sec = '0'+sec;

    var res =second=true?hr+":"+min:hr+":"+min+":"+sec;
    return res;
}

async function clickBook()
{
    var today = new Date()
    var start_time= formatDate(today)+" "+formatTime(today,false);
    var end_time = formatDate(today)+" "+today.getHours()+1+":00:00";
    var formData = new FormData();
    formData.append('start_time',start_time)
    formData.append('end_time',end_time)
    formData.append('study_table_id',8)
    await axios({
        method: "POST",
        url: "http://127.0.0.1:5000/booking/tapBooking",
        data: formData,
        headers: { "Content-Type": "multipart/form-data" },
    })
    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
        if(res.statusCode===201)
            window.location.href="kit_dashboard.html";
    })
}

async function removeBooking()
{
    let formData = new FormData();
    formData.append('booking_id',2);
    await axios({
        method: "DELETE",
        url: "http://127.0.0.1:5000/booking/",
        data: formData,
        headers: { "Content-Type": "multipart/form-data" },
    })
    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
        if(res)
        {
            window.location.href = "kit_available.html";
        }
    })
}

async function updateNextHour()
{
    setInterval(function(){
        let endTime = new Date();
        document.getElementById("nextHour").innerHTML = formatHr(endTime.getHours()+1)+":00";
    },1000);
}

function countDown()
{
    let startTime = new Date();
    let endTime = new Date();
    document.getElementById("start").innerHTML = formatTime(startTime,true);
    document.getElementById("end").innerHTML = formatHr(endTime.getHours()+1)+":00";
    setInterval(function(){
        var currHr = new Date().getHours();
        if(currHr-startTime.getHours()===1)
        {
            clearInterval(countDown);
            document.getElementById('checkout').click();
        }
      },1000); 
}

async function enterDetail()
{
    event.preventDefault()
    let mac = document.getElementById("mac").value;
    let formData = new FormData()

    formData.append('mac_address',mac)
    await axios({
        method: "POST",
        url: "http://127.0.0.1:5000/studyTable/getInfo",
        data: formData,
        headers: { "Content-Type": "multipart/form-data" },
    })

    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
        console.log(res)
        if(res.result.study_table_id!==null)
        {
            window.location.href= "kit_available.html"
        }
    })
}

async function checkAvailable(tableId)
{
    let formData = new FormData();
    let today = new Date();
    let startTime = formatDate(today)+" "+today.getHours()+":00:00";
    let endTime = formatDate(today)+" "+today.getHours()+1+":00:00";
    let table_id = 8;
    formData.append('startTime',"2021-10-27 19:36:00");
    formData.append('endTime','0000-00-00 00:00:00');
    formData.append('tableId',table_id);
    await axios({
        method: "POST",
        url: "http://127.0.0.1:5000/booking/tableBooking",
        data: formData,
        headers: { "Content-Type": "multipart/form-data" },
    })
    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
       console.log(res)     
    })
}

function checkHourly(tableId)
{
    setInterval(function(){
        checkAvailable(tableId)
    },3600000)
}