//Developed by Kevin with contributions by Jeremy
function formatHr(hour){
    hour = hour<10?'0'+hour:hour;
    return hour;
}

function formatDate(today)
{
    var mon = today.getMonth()+1;
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
    var start_time= formatDate(today)+" "+today.getHours()+":00:00";
    var end_time = formatDate(today)+" "+parseInt(today.getHours()+1)+":00:00";
    var formData = new FormData();
    formData.append('start_time',start_time)
    formData.append('end_time',end_time)
    await axios({
        method: "POST",
        url: "/booking/tapBooking",
        data: formData,
        headers: { "Content-Type": "multipart/form-data" },
    })
    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
        if(res.statusCode===201)
            window.location.href="/tableKit/claimed";
    })
}

async function removeBooking(isCheckout)
{
    let formdata = new FormData();
    formdata.append('isCheckout',isCheckout);
    await axios({
        method: "DELETE",
        url: "/booking/",
        data: formdata,
        headers: { "Content-Type": "multipart/form-data" },
    })
    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
        if(res)
        {
            window.location.href = "/tableKit/available";
        }
    })
}

function updateNextHour()
{
        let endTime = new Date();
        document.getElementById("nextHour").innerHTML = formatHr(endTime.getHours()+1)+":00";
}

function countDown(endTime)
{
    let startTime = new Date();
    document.getElementById("start").innerHTML = formatTime(startTime,true);
    setInterval(function(){
        var currHr = new Date().getHours();
        if(currHr===endTime)
        {
            clearInterval(countDown);
            window.location.href = "/tableKit/available"
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
        url: "/studyTable/getInfo",
        data: formData,
        headers: { "Content-Type": "multipart/form-data" },
    })

    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
        if(res.result.study_table_id!==null)
        {
            window.location.href= "/tableKit/available";
        }
    })
}

async function checkAvailable(tableId)
{
    let formdata = new FormData();
    let today = new Date();
    let startTime = formatDate(today)+" "+today.getHours()+":00:00";
    formdata.append('startTime',startTime);
    formdata.append('tableId',tableId)
    await axios({
        method: "POST",
        url: "/booking/tableBooking",
        data: formdata,
        headers: { "Content-Type": "multipart/form-data" },
    })
    .then(res=>res.data)
    .catch(err=>console.log(err))
    .then(res=>{
            if (res!==null)
            {
                window.location.href = "/tableKit/reserved"
            }
    })
}

function checkHourly(tableId)
{
    today = new Date().getHours();
    checkAvailable(tableId);
    setInterval(function(){
        currHr = new Date().getHours();
        if(currHr-today===1)
            checkAvailable(tableId)
            today = currHr
        updateNextHour()
    },1000)
}

function clickNumPad(num)
{
        document.getElementById("passcodeField").value += num;
}

async function verifyBooking()
{
        event.preventDefault();
        let formdata = new FormData();
        let passcode = document.getElementById("passcodeField").value;
        formdata.append('passcode',passcode);
        await axios({
        method: "POST",
        url: "/booking/verify",
        data: formdata,
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then(res=>res.data)
      .catch(err=>console.log(err))
      .then(res=>{
            if(res.result===true)
            {
                   window.location.href= "/tableKit/claimed";
            }
      })
}
function checkUserClaimed()
{
        setInterval(function(){
                let currTime = new Date();
                if(currTime.getMinutes()>=15)
                {
                    removeBooking(false);
                }
        },1000)
}
