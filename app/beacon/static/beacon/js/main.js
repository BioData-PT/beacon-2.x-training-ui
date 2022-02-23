(function(){ // scoping

    // Datatables
    $(document).ready( function () {
        $('#table_id').DataTable({
            "searching": false
        });
    } );


    // Login/logout mock up
    var loginButton = $("#login");
    var tableWrapper = $(".table-wrapper.controlled");
    var countsResult = $("section#counts p");
    var errorLogin = $("span.error-login");

    loginButton.on("click", function(){
        tableWrapper.toggleClass("blurry");
        countsResult.toggleClass("blurry");
        errorLogin.toggleClass("active");
        $(this).text(function(i, text){
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


})();
