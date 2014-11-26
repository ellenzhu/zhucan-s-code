/* global $ */

$(function() {
    "use strict";
    // We add a live event handler that handles clicking any link inside #continentMenu.
    // See: http://api.jquery.com/live/
    $("#continentMenu a").live("click", function() {
        // Take the target url from the link that was clicked
        var url = $(this).attr("href");
        
        // Change the title with id continentName to the text in the clicked link
        $("#continentName").text($(this).text());
        
        // Replace the contents of #tableContainer with data 
        // that is dynamically from the link's target url
        $("#tableContainer").load(url);
        
        // Return false to prevent the default behavior of "click" (changing the page)
        return false;
    });
});
