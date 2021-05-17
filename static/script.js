'use strict';
window.addEventListener('load', function () {
  document.getElementById('sign-out').onclick = function() {
   // ask firebase to sign out the user
   firebase.auth().signOut();
  };
var uiConfig = {
 signInSuccessUrl: '/',
 signInOptions: [
 firebase.auth.GoogleAuthProvider.PROVIDER_ID,
 firebase.auth.EmailAuthProvider.PROVIDER_ID
 ]
};
firebase.auth().onAuthStateChanged(function(user) {
 if(user) {
 document.getElementById('sign-out').hidden = false;
 document.getElementById('login-info').hidden = false;
  document.getElementById('nav').hidden = false;

 console.log('Signed in as ${user.displayName} (${user.email})');
 user.getIdToken().then(function(token) {
 document.cookie = "token=" + token;
 });
 } else {
 var ui = new firebaseui.auth.AuthUI(firebase.auth());
 ui.start('#firebase-auth-container', uiConfig);
 document.getElementById('sign-out').hidden = true;
 document.getElementById('login-info').hidden = true;
   document.getElementById('nav').hidden = true;
 document.cookie = "token=";
 }
 }, function(error) {
 console.log(error);
 alert('Unable to log in: ' + error);
 });

     var dtToday = new Date();

     var month = dtToday.getMonth() + 1;
     var day = dtToday.getDate();
     var year = dtToday.getFullYear();
     if(month < 10)
         month = '0' + month.toString();
     if(day < 10)
         day = '0' + day.toString();

     var maxDate = year + '-' + month + '-' + day;
     $('#txtDate1').attr('min', maxDate);
     $('#txtDate2').attr('min', maxDate);
     $('#txtDate3').attr('min', maxDate);
     $('#txtDate4').attr('min', maxDate);
     $('#txtDate5').attr('min', maxDate);
     $('#txtDate6').attr('min', maxDate);
     $('#txtDate1').change(function(){
       var thisdate = this.value.split('-');
       var date= parseInt(thisdate[2])+1
       var newdate = thisdate[0] +'-'+ thisdate[1] +'-'+ date

       $('#txtDate2').attr('min', newdate);
    });
    $('#txtDate3').change(function(){

       var thisdate = this.value.split('-');
       var date= parseInt(thisdate[2])+1
       var newdate = thisdate[0] +'-'+ thisdate[1] +'-'+ date

       $('#txtDate4').attr('min', newdate);
   });
   $('#txtDate5').change(function(){

      var thisdate = this.value.split('-');
      var date= parseInt(thisdate[2])+1
      var newdate = thisdate[0] +'-'+ thisdate[1] +'-'+ date

      $('#txtDate6').attr('min', newdate);
  });

});
window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove();
    });
}, 6000);
