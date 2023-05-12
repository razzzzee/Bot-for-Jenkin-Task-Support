var applicationConfig = {
    clientID: "e2f8dcc0-077b-45cb-b905-5969bee4e9e0",
    authority: "https://login.microsoftonline.com/common",
    graphScopes: ["user.read"],
    graphEndpoint: "https://graph.microsoft.com/v1.0/me"
};



$(document).ready(function(){    
    if(sessionStorage.loginUserName){
      loginSuccess(sessionStorage.loginUserName);  
    }
   });


function loadForm(form)
{
    if(form == "home"){
        $('#home').show();
        $('#chat').hide();
        $('#contact').hide();
    }else if(form == "chat"){
        $('#home').hide();
        $('#chat').show();
        loadJobs();
        $('#contact').hide();
    }
    else if(form == "contact"){
        $('#home').hide();
        $('#chat').hide();
        $('#contact').show();
    }
}

function loginSuccess(user){
   
    
    //if successful
    sessionStorage.loginUserName=user;
    $("#regLoginMenu").hide();
    
    //$("#displayLoginUsernameLI").text("Username");
    
    document.getElementById("displayLoginUsername").innerHTML=sessionStorage.loginUserName;
    
    $("#displayLoginUsernameMenu").show();
    $("#chatMenu").show();    
}


function onLogout(){
    signOut();
    document.getElementById("displayLoginUsername").innerHTML="";
    $("#displayLoginUsernameMenu").hide();
    $("#regLoginMenu").show();
    $("#chatMenu").hide();
    $('#home').show();
    $('#chat').hide();
    sessionStorage.removeItem("loginUserName");
    history.go(0);
    window.location.href = window.location.href;
    // $('#contact').hide();
}

function loadJobs(){
    var jobArray=["1. What is the latest changeset on Dev env?",
                  "2. Promote latest Dev build to QA env",
                  "3. Deploy <ChangesetID> changeset on Int env",
                  "4. What is the status of Dev Smoke?",
                  "5. Give me the status of QA Regression",
                  "6. Fetch me the status of User TestSuite job on Dev", 
                  "7. What is the status of Automation TestSuite Job on QA env", 
                  "8. Start regression on QA",
                  "9. Trigger Master_HealthCheck Job on Int env",
                  "10. Trigger Automation TestSuite job on QA env",
                  "11. Invoke Smoke Suite on Int environment"];
    $("#jobsUL").empty();
    jobArray.forEach(function(job){
        $("#jobsUL").append('<li class="list-group-item">'+job+'</li>');
        
    });
}


var myMSALObj = new Msal.UserAgentApplication(applicationConfig.clientID, null, acquireTokenRedirectCallBack,
    {storeAuthStateInCookie: true, cacheLocation: "localStorage"});

function signIn() {
    myMSALObj.loginPopup(applicationConfig.graphScopes).then(function (idToken) {
        //Login Success
        //showWelcomeMessage();
        acquireTokenPopupAndCallMSGraph();
    }, function (error) {
        console.log(error);
    });
}

function acquireTokenPopupAndCallMSGraph() {
    //Call acquireTokenSilent (iframe) to obtain a token for Microsoft Graph
    myMSALObj.acquireTokenSilent(applicationConfig.graphScopes).then(function (accessToken) {
        callMSGraph(applicationConfig.graphEndpoint, accessToken, graphAPICallback);
    }, function (error) {
        console.log(error);
        // Call acquireTokenPopup (popup window) in case of acquireTokenSilent failure due to consent or interaction required ONLY
        if (error.indexOf("consent_required") !== -1 || error.indexOf("interaction_required") !== -1 || error.indexOf("login_required") !== -1) {
            myMSALObj.acquireTokenPopup(applicationConfig.graphScopes).then(function (accessToken) {
                callMSGraph(applicationConfig.graphEndpoint, accessToken, graphAPICallback);
            }, function (error) {
                console.log(error);
            });
        }
    });
}

function graphAPICallback(data) {
    response = JSON.stringify(data, null, 2);
    loginSuccess(data.userPrincipalName);
}

// This function can be removed if you do not need to support IE
function acquireTokenRedirectAndCallMSGraph() {
    //Call acquireTokenSilent (iframe) to obtain a token for Microsoft Graph
    myMSALObj.acquireTokenSilent(applicationConfig.graphScopes).then(function (accessToken) {
      callMSGraph(applicationConfig.graphEndpoint, accessToken, graphAPICallback);
    }, function (error) {
        console.log(error);
        //Call acquireTokenRedirect in case of acquireToken Failure
        if (error.indexOf("consent_required") !== -1 || error.indexOf("interaction_required") !== -1 || error.indexOf("login_required") !== -1) {
            myMSALObj.acquireTokenRedirect(applicationConfig.graphScopes);
        }
    });
}

function acquireTokenRedirectCallBack(errorDesc, token, error, tokenType)
{
 if(tokenType === "access_token")
 {
     callMSGraph(applicationConfig.graphEndpoint, token, graphAPICallback);
 } else {
     console.log("token type is:"+tokenType);
 }
}


// Browser check variables
var ua = window.navigator.userAgent;
var msie = ua.indexOf('MSIE ');
var msie11 = ua.indexOf('Trident/');
var msedge = ua.indexOf('Edge/');
var isIE = msie > 0 || msie11 > 0;
var isEdge = msedge > 0;

//If you support IE, our recommendation is that you sign-in using Redirect APIs
//If you as a developer are testing using Edge InPrivate mode, please add "isEdge" to the if check
if (!isIE) {
    if (myMSALObj.getUser()) {// avoid duplicate code execution on page load in case of iframe and popup window.
        //showWelcomeMessage();
        acquireTokenPopupAndCallMSGraph();
    }
}
else {
    document.getElementById("SignIn").onclick = function () {
        myMSALObj.loginRedirect(applicationConfig.graphScopes);
    };
    if (myMSALObj.getUser() && !myMSALObj.isCallback(window.location.hash)) {
        acquireTokenRedirectAndCallMSGraph();
    }
}

function callMSGraph(theUrl, accessToken, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200)
            callback(JSON.parse(this.responseText));
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader('Authorization', 'Bearer ' + accessToken);
    xmlHttp.send();
}

 function signOut() {
     myMSALObj.logout();
 }