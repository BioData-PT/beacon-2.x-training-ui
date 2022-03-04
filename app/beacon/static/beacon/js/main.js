(function(){ // scoping

    
    // Cookie Functions
    function setCookie(name,value,minutes) {
        if (minutes) {
            var date = new Date();
            date.setTime(date.getTime()+(minutes*60*1000));
            var expires = "; expires="+date.toGMTString();
        } else {
            var expires = "";
        }
        document.cookie = name+"="+value+expires+"; path=/";
    }

    // Datatables
    $(document).ready( function () {
        $('.results-table').DataTable({
            "searching": false
        });
    } );

    // Table type selection
    var radioButtons = $("div#table-type div input");
    var tables = $("div.table-wrapper");

    radioButtons.on("click", function(){
        // radioButtons.prop('checked', false);
        me = $(this);
        // me.prop('checked', true);
        var tableType = me.val();
        tables.removeClass("active");
        $("div.table-wrapper." + tableType).addClass("active");
    });


    // Login/logout mock up
    var loginButton = $("#login");
    var controlledItem = $(".controlled");
    var countsResult = $("section#counts p");
    var errorLogin = $("span.error-login");
    var cookieValue = "";

    loginButton.on("click", function(){
        controlledItem.toggleClass("blurry");
        countsResult.toggleClass("blurry");
        errorLogin.toggleClass("active");
        $(this).text(function(i, text){
            // cookie
            text === "LOG IN" ? cookieValue = "true" : cookieValue = "false";
            setCookie("loggedIn", cookieValue, 5);
            // console.log(cookieValue);
            // toggle text
            return text === "LOG IN" ? "LOG OUT" : "LOG IN";
        })
    });


    // Navbar
    // When the user scrolls down 80px from the top of the document, resize the navbar's padding and the logo's font size
    var navbar = $("nav");
    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
        if (document.body.scrollTop > 55 || document.documentElement.scrollTop > 55) {
            navbar.addClass("shadow");
        } else {
            navbar.removeClass("shadow");
        }
    }; 

    // Results tabs
    var tabs = $("#tabs p");
    var resultSections = $(".results section");

    tabs.on("click", function(){

        var me = $(this);

        // select tab
        tabs.removeClass("active");
        me.addClass("active");

        // choose result
        targetResult = me.attr("attr-target");
        resultSections.removeClass("active");
        $("#" + targetResult).addClass("active");

    });

    // Format JSON
    // https://www.cssscript.com/minimal-json-data-formatter-jsonviewer/ 

    // Example
    // Add <div id="json"></div> somewhere to test it
    // var jsonObj = {};
    // var jsonViewer = new JSONViewer();
    // document.querySelector("#json").appendChild(jsonViewer.getContainer());

    // testString = JSON.stringify([{'assayCode': {'id': 'LOINC:35925-4', 'label': 'BMI'}, 'date': '2021-09-24', 'measurementValue': {'units': {'id': 'NCIT:C49671', 'label': 'Kilogram per Square Meter'}, 'value': 28.17336761}}, {'assayCode': {'id': 'LOINC:3141-9', 'label': 'Weight'}, 'date': '2021-09-24', 'measurementValue': {'units': {'id': 'NCIT:C28252', 'label': 'Kilogram'}, 'value': 94.9065}}, {'assayCode': {'id': 'LOINC:8308-9', 'label': 'Height-standing'}, 'date': '2021-09-24', 'measurementValue': {'units': {'id': 'NCIT:C49668', 'label': 'Centimeter'}, 'value': 183.5391}}]);
    // jsonObj = JSON.parse(testString);
    // console.log(testString);
    // console.log(jsonObj)
    // jsonViewer.showJSON(jsonObj, null, 1);
    // End Example

    $("td div.json").each(function() {
        var jsonObj = {};
        var jsonViewer = new JSONViewer();
        this.appendChild(jsonViewer.getContainer());
        
        data = $( this ).attr("attr-data").replace(/'/g, '"');;
        
        try {
            jsonObj = JSON.parse(data);
            jsonViewer.showJSON(jsonObj, null, 2);
        }
        catch (err) {
            // console.log(err);
            $(this).text(data);
        }
      });

})();
