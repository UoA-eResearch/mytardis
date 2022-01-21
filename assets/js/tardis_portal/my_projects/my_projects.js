import {attachProjAccordionClickHandlers, loadLatestExpSummary, expandFirstProjects} from "../project-accordion";
$(document).ready(function() {
    // Load owned exps on page load
    var loadingHTML = "<img src=\"/static/images/ajax-loader.gif\"/><br />";
    $("#myprojects").html(loadingHTML);
    $("#myprojects").load(
        "/ajax/owned_proj_list/",
        function() {
            attachProjAccordionClickHandlers("accordion-toggle", "toggle-", "collapse-", "latest-exp-", loadLatestExpSummary);
            expandFirstProjects();

            $(".explink").on("click", function(evt) {
                evt.stopPropagation();
            });
            $(".dllink").on("click", function(evt) {
                evt.stopPropagation();
            });
        });

    // Create a reload event handler
    $("#myprojects").on("reload", function() {
        $(this).html(loadingHTML);
        $(this).load(
            "/ajax/owned_proj_list/",
            function() {
                attachProjAccordionClickHandlers("accordion-toggle", "toggle-", "collapse-", "latest-exp-", loadLatestExpSummary);
                expandFirstProjects();

                $(".explink").on("click", function(evt) {
                    evt.stopPropagation();
                });
                $(".dllink").on("click", function(evt) {
                    evt.stopPropagation();
                });
            });
    });

    // var attachProjAccordionClickHandlers = function(accordionToggleClass, accordionToggleIdPrefix, accordionBodyIdPrefix, divIdPrefix, loadDatasetsSummary)
    attachProjAccordionClickHandlers("accordion-toggle", "toggle-", "collapse-", "latest-exp-", loadLatestExpSummary);
    expandFirstProjects();
});

$(document).on("click", ".page-link", function() {
    var loadingHTML = "<img src=\"/static/images/ajax-loader.gif\"/><br />";
    var href = $(this).attr("href");
    $(this).html(loadingHTML);
    $("#myprojects").load(href, function() {
        attachProjAccordionClickHandlers("accordion-toggle", "toggle-", "collapse-", "latest-exp-", loadLatestExpSummary);
        expandFirstProjects();
    });
    return false;
});
