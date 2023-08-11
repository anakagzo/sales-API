// --------------------Product section--------------------\\ 
// make the info card to disappear after 8 seconds
document.addEventListener('DOMContentLoaded', function () {
    // Hide the div after the page has loaded

    var card = document.getElementById('infoCard');

    // Change the timeout duration (in milliseconds) 
    var timeoutDuration = 8000; // 8 seconds


    setTimeout(function() {
        card.style.visibility = "hidden";
        }, timeoutDuration);

        
});


// Confirm that the user wants to delete all products, after clicking the 'delete all products '
function showConfirmation1() {
    var result = window.confirm("Are you sure you want to proceed?.You can export your data before proceeding.");
    if (result) {
        // User clicked "Yes"
        var delbtn = document.getElementById('delAllProducts');
        delbtn.click()
    } else {
        // User clicked "No" or closed the confirmation
        
    }
    }


// show file dialog box after user clicks 'import products'
function showdialog() {
    document.getElementById('input_excel').click();
    var inputfile = document.getElementById('input_excel');
    
    
    inputfile.addEventListener('change',function(){
    document.getElementById('import_excel').submit();
    });
    }


// download the database excel sheet just after loading the page
window.onload = function myfunc() {
    document.getElementById('download').click();
    }


// show the name of image file after the user selects an image file
function showInfo1() {
    document.getElementById('image').click();
    var imgfile = document.getElementById('image');
    
    
    imgfile.addEventListener('change',function(){
    var imgInfo = document.getElementById('img_info');
    imgInfo.style.display = "inline"
    imgInfo.textContent = imgfile.value
    });
    }


// --------------------Tips section--------------------\\ 

// Confirm that the user wants to delete all tips, after clicking on 'delete all tips ' 
function showConfirmation2() {
    var result = window.confirm("Are you sure you want to proceed?.All tips will be wiped out.");
    if (result) {
        // User clicked "Yes"
        var delbtn = document.getElementById('delAllTips');
        delbtn.click()
    } else {
        // User clicked "No" or closed the confirmation
        
    }
    }

// show the name of image file after the user selects an image file
function showInfo2() {
    document.getElementById('image').click();
    var imgfile = document.getElementById('image');
    
    
    imgfile.addEventListener('change',function(){
    var imgInfo = document.getElementById('img_info');
    imgInfo.style.display = "inline"
    imgInfo.textContent = imgfile.value
    });
    }


