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

    $(document).ready( function () {
        $('.basic-table').DataTable({
            "searching": false,
            "paging": false
        });
    } );


    // Searchable DataTable config
    $('.searchable-table thead tr.search-tr th.search-box').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );

    $('.searchable-table').DataTable({
        // "searching": false,
        "paging": false,
        initComplete: function () {
            // Apply the search
            this.api().columns().every( function () {
                var that = this;
 
                $( 'input', this.header() ).on( 'keyup change clear', function () {
                    if ( that.search() !== this.value ) {
                        that
                            .search( this.value )
                            .draw();
                    }
                } );
            } );
        }
    });


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
    //// When the user scrolls down 80px from the top of the document, resize the navbar's padding and the logo's font size
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
    //// https://www.cssscript.com/minimal-json-data-formatter-jsonviewer/ 
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


    // Examples
    //// put example on query box when clicking it
    var example = $("p.example");
    var query = $("form input[type='text']");
    var select = $("form select");

    example.on("click", function(){
    if ($(this).hasClass("phenoclinic")) {
        console.log("phenoclinic");
        text = $(this).text().split(" and ");
        target = text[0];
        queryValue = text[1];
        console.log(target)
        console.log(queryValue)
        select.val(target).change();
        query.val(queryValue);
        $('form select option').removeAttr('selected').filter('[value='+target+']').attr('selected', true)
    } else {
        console.log("basic");
        query.val($(this).text());
        }
    });

    // Filtering terms selection
    var checkboxTd = $("table.searchable-table td.checkbox");
    var clipboardButton = $("#clipboard-terms i");
    var clipboardText = $("#clipboard-terms input");
    var selectedTerms = [];

    checkboxTd.on("click", function(){
        me = $(this);
        var checkboxIcon = me.find("i");
        var term = me.next("td").text();
        if (checkboxIcon.hasClass("fa-square-o")) { // aka not selected
            checkboxIcon.removeClass("fa-square-o");
            checkboxIcon.addClass("fa-check-square-o");
            // add to selectedTerms
            selectedTerms.push(term);
        } else {
            checkboxIcon.removeClass("fa-check-square-o");
            checkboxIcon.addClass("fa-square-o");
            // remove from selectedTerms
            selectedTerms.splice($.inArray(term, selectedTerms), 1);
        };
        clipboardText.val(selectedTerms.join(", "));
    });

    //// clipboard https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Interact_with_the_clipboard
    function copy() {
        clipboardText.select();
        document.execCommand("copy");
    };
    clipboardButton.on("click", copy);
    
    //// clean all selections
    var checkboxTh = $("table.searchable-table th.checkbox");
    var checkboxTdIcons = $("table.searchable-table td.checkbox i");
    checkboxTh.on("click", function(){
        checkboxTdIcons.removeClass("fa-check-square-o");
        checkboxTdIcons.addClass("fa-square-o");
        selectedTerms = [];
        clipboardText.val("");
    });

})();
