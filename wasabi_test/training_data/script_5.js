//config code
var company_name = "Metropolitan Transportation Authority";
// .header-outer height
var top_offset_height = 0;

// Set height
function setHeight(the_selector) {
    var a_height = 0;
    $(the_selector).css('height','auto');
    if ($(window).width() > 620) {
        $(the_selector).each(function() {
        if ($(this).outerHeight() > a_height) {
            a_height = $(this).outerHeight();
        }
        });
        $(the_selector).attr('style','height: '+a_height+'px;');
    }
}

// Responsive videos
function setrespvideos() {
    var $allVideos = $("iframe[src^='https://player.vimeo.com'], iframe[src^='https://www.youtube.com'], iframe[src^='http://player.vimeo.com'], iframe[src^='http://www.youtube.com'], object, embed").not('.no-resize-video');
    $allVideos.each(function() {
        $(this).attr('data-aspectRatio', this.height / this.width).removeAttr('height').removeAttr('width');
    });
    $(window).resize(function() {
        $allVideos.each(function() {
        newHeight = $(this).width() * $(this).attr('data-aspectRatio');
        $(this).attr('style','height: '+newHeight+'px !important');
        });
    }).resize();
}

// Google Locations Look-Up + Google Maps
/*csns.maps.script.channel = "";
csns.maps.script.client_id = null;
csns.maps.script.api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
csns.maps.script.version = 3.23;*/
function tm_split_url_maps(full_url){
    var urls = full_url.split("?");
    var search_path = urls[0] + ".json";
    if(search_path=="/.json"){
        search_path = "/search/jobs.json";
    }
    var search_params = urls[1];
    if(search_params && search_params.length > 1) {
        search_params = "data_format=map&" + search_params;
    }
    else {
        search_params = "data_format=map";
    }
    return [search_path, search_params];
}
function is_maps_url_different(search_path, search_params){
    return (csns.maps.jobs_map_default.markers_url!=search_path && csns.maps.jobs_map_default.markers_url_search != search_params)
}
function tm_split_url_maps_set(full_url){
    var srch = tm_split_url_maps(full_url);
    var search_path = srch[0];
    var search_params = srch[1];

    if(is_maps_url_different(search_path, search_params)==false){
        csns.maps.jobs_map_default.markers_url = search_path;
        csns.maps.jobs_map_default.markers_url_search = search_params;
        if(typeof(jobsmap) !== "undefined" && jobsmap!=null){
            jobsmap.markers_url = search_path;
            jobsmap.markers_url_search = search_params;
        }
    }
}
function tm_maps_clear(){
    if(typeof(jobsmap) !== "undefined" && jobsmap!=null) {
        if(jobsmap.markers!=null && jobsmap.markerclusterer!=null){
            jobsmap.markerclusterer.removeMarkers( jobsmap.markers )
            jobsmap.markers = [];
        }
    }
}
function tm_maps_reload(){
    if(typeof(jobsmap) !== "undefined" && jobsmap!=null) {
        google.maps.event.trigger(jobsmap.map, 'resize');
        window.setTimeout(function(){
            google.maps.event.trigger(jobsmap.map, 'resize');
            tm_maps_clear();
            tm_maps_set_all_results();
            //jobsmap.draw_map("gmapfvxip", null);
            //google.maps.event.trigger(jobsmap.map, 'resize');
            jobsmap.draw_map("gmapfvxip", null);
        }, 400);
    }
}
function tm_maps_set_all_results(){
    if(typeof(jobsmap) !== "undefined" && jobsmap!=null) {
        var totaljobs = parseInt( $("#totalresults").html() );
        jobsmap = new csns.maps.jobs_map();
        if(totaljobs > 700) {
            jobsmap.all_results=false;
        }
        else {
            jobsmap.all_results=true;
        }
    }
}
function tm_maps_refresh(){
    if(typeof(jobsmap) !== "undefined" && jobsmap!=null){
        google.maps.event.trigger(jobsmap.map, 'resize');
        jobsmap.map.fitBounds( jobsmap.bounds );
    }
}
function tm_refesh_map(visible){
    if(visible==true){
        if(jobsmap == null) {
            tm_init_jobsmap();
        }
        else {
            tm_maps_refresh();
        }
    }
}
var jobsmap = null;
function pinbackmap() {
    try{
        csns.maps.script.load( function(){
            var cslocations = $cs.parseJSON('');
            jobsmap = new csns.maps.jobs_map();
            tm_maps_set_all_results();
            jobsmap.draw_map("gmapfvxip", cslocations);
        });
    }catch(e){ console_log_info(e) }
}
$(document).ready(function(){ tm_initialize_search_form(); });
//// ### TM functions
function tm_initialize_search_form(){
    var selectors = window.tmjobsearch.form_defaults.input_selectors;
    selectors.ns_location = "input[type=text][name=ns_location]";
    
    if($("#search_form").length>0){
        var comprest = {}
        var jobform = new window.tmjobsearch.form("search_form", {
        radius_distance_in_miles: tm_vars.radius_in_miles,
        radius_distance_default: 25,
        radius_distance: tm_vars.param_ns_dist,
        onSubmit: function(e){
            window.setTimeout( tm_form_submit , 100);
            return false;
        },
        placeTypes: ['geocode'],
        placeComponentRestrictions: comprest,
        onBeforePlaceLoad: function(place, radius, location_string){
            return [place, radius, location_string];
        }
        });
    }
}
function tm_form_submit(){
    $("#submit_search").empty();
    var jsform = $("#search_form");
    
    var q = jsform.find("input[name=q]").val();
    tm_append_input_value_to_submit_search('q', q);
    
    var searchfieldname = [];
    $('.search-field').each(function(index) {
        searchfieldname[index] = $(this).attr('name');
        var searchfield = jsform.find(this).val();
        tm_append_input_value_to_submit_search(searchfieldname[index], searchfield);
    });
    
    var radius = jsform.find( window.tmjobsearch.form_defaults.input_selectors.radius).val();
    var mks = $("input[name=ns_mk]:checked").val();
        
    var dist = parseInt($("#job-search-radius").val());
    var dists = isNaN(dist) ? 25 : dist;
    
    var newwithin = "";
    if(radius!="" && radius.indexOf(",,")<0){
        var lat = radius.split(",")[0];
        var long = radius.split(",")[1];
        newwithin = "/within/"+dists+"/"+mks+"/of/"+lat+"/"+long;
    }else{
        var dist = parseInt($("#job-search-radius").val());
        dist = dist ? dist : 25;
        var mk = $("input[name=ns_mk]:checked").val();
        if(mk=="km"){
        if(dist!=25){ //dont submit default
            tm_append_input_value_to_submit_search('near_dist_km', dist);
        }
        }else if(mk=="mi"){
        tm_append_input_value_to_submit_search('near_dist_miles', dist);
        }
    
        var location_country = jsform.find( window.tmjobsearch.form_defaults.input_selectors.location_country).val();
        tm_append_input_value_to_submit_search('location_country', location_country);
        var location_state = jsform.find( window.tmjobsearch.form_defaults.input_selectors.location_state).val();
        tm_append_input_value_to_submit_search('location_state', location_state);
        var location = jsform.find( window.tmjobsearch.form_defaults.input_selectors.location).val();
        tm_append_input_value_to_submit_search('location', location);
    }
    
    var action = $("#submit_search").attr("action");
    if(action.indexOf("/within") >= 1){
        action = action.replace(/\/within\/[\w\.\/]+of\/[\-\w\.]+\/[\-\w\.]+/, newwithin);
    }else{
        action += newwithin;
    }
    $("#submit_search").attr("action", action);
    
    var ns_location = jsform.find("input[name=ns_location]").val();
    tm_append_input_value_to_submit_search('ns_location', ns_location);
    
    var per_page = jsform.find("input[name=per_page]").val();
    if(per_page!=null && per_page!="" && per_page!="25"){
        tm_append_input_value_to_submit_search('per_page', per_page);
    }
    
    var sort_by = jsform.find("input[name=sort_by]").val();
    if(sort_by!="" && sort_by!=DEFAULT_SORT){
        tm_append_input_value_to_submit_search('sort_by', sort_by);
    }
    tm_finish_submit();
}
function tm_append_input_value_to_submit_search(name, val){
    if(name!=null && name!="" && val!=null && val!=""){
        var t_input = $("<input type='hidden'/>");
        t_input.attr("name", name);
        t_input.val(val);
        $("#submit_search").append(t_input);
    }
}
function tm_finish_submit(keywords, location){
    var url = url_from_form("#submit_search");
    
    tm_get_jobs_ajax(url, "search");
}
// MAIN AJAX job function
function tm_get_jobs_ajax(url, ajax_event_name){
    window.location.href = url;
}
function tm_event_jobs_ajax_start(full_url, ajax_event_name){
    $(document.body).addClass("tm_loading");
    $("#tm_job_results_toggle_tabs").hide();
    $("#tm_job_results_options").hide();
    tm_scroll_to("#tm_job_results_header");
}
function url_from_form(form_selector){
    var url = null;
    var form = $(form_selector);
    if(form.length>0){
        var action = form.attr("action");
        var query = form.serialize();
        url = action;
        if(query.length>0){
        url += "?" + query;
        }
    }
    return url;
}
var DEFAULT_SORT = "score";
//// ### COOKIE FUNCTIONS
function setCookie(name,value,days) {
    var expires="";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        expires = "; expires="+date.toGMTString();
    } else {
        //ie 11 is Netscape
        if (navigator.appName != "Microsoft Internet Explorer" &&
        navigator.appName != "Netscape"){
        expires = ";expires=0";
        }
    }
    document.cookie = name+"="+value+";path=/"+expires;
}
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}
//// ### END Cookie functions

// Facet code 1
window.facet_history = true;
// Function for expanding/collapsing Facet options
function facet_expand_collapse(facet_item_this){
    facet_item_this.parent().next('.facet-item__options').slideToggle();
    facet_item_this.parents('.facet-item').toggleClass('facet-item--expanded facet-item--collapsed');
}
// Function for Ajax-ing Job Search Results
function ds_tm_get_jobs_ajax(url){
    window.facet_loading = true;
    
    var t = $(".jobs-section").offset().top - (top_offset_height+$('.jobs-category-section').outerHeight());
    t = t > 0 ? t : 1;

    $('.preloader--search').show().find('.facet-jobs-loading').fadeIn().attr('tabindex','0').focus();
    $('.jobs-section__inner').hide().find('.facet-jobs-loaded').fadeOut();
    
    if(window.facet_history==true && window.history!=null && window.history.pushState!=null){
        window.history.pushState({},"",url);
    }
    
    $.get(url, function(data) {
        $(".jobs-category-section").html( $(data).find('.jobs-category-section').html() );
        $(".jobs-category-banner").html( $(data).find('.jobs-category-banner').html() );
        $(".jobs-heading").html( $(data).find('.jobs-heading').html() );
        $(".facet-section").html( $(data).find('.facet-section').html() );
        $(".jobs-section").html( $(data).find('.jobs-section').html() );

        var tagtitle = $(data).filter('title').text();
        document.title = (tagtitle!="") ? tagtitle : company_name+" Careers";
            
        $(".jobs-section__list").hide();
        $(".jobs-section__list").fadeIn(500);

        $('.facet-section').removeClass("ds_tm_ff_wait");
        window.facet_loading = false;
    
        if ($('.jobs-section__map.active').length > 0) {
            tm_split_url_maps_set(url);
            tm_maps_reload();
        }
        $('.preloader--search').hide();
        $('.jobs-section__inner').show();

        $('html, body').animate({scrollTop: t}, 400, 'swing');

        $('.facet-jobs-loading').fadeOut();
        $('.facet-jobs-loaded').fadeIn().attr('tabindex','0').focus();

        $('.jobs-section__paginate .prev_page').html('<img src="/system/production/assets/357052/original/pagination-prev.png">');
        $('.jobs-section__paginate .next_page').html('<img src="/system/production/assets/357051/original/pagination-next.png">');
    });
}
function ds_tm_facet_click(e){
    e.preventDefault();
    var l = $(e.target).closest(".facet-item__option-link");

    if(window.facet_loading==true) {
        $('.facet-section').addClass("ds_tm_ff_wait");
    }
    else {
        l.addClass("ds_tm_ff_loading");
        $('.facet-section').addClass("ds_tm_ff_wait");

        var url = l.attr("href");
        ds_tm_get_jobs_ajax(url);
    }
} 
// Function to showing more Facet options over the facet_num_limit
function ds_tm_facet_more_click(e){
    var l = $(e.target).closest(".facet-item__show-more");
    var facetname = l.attr("ref");
    $("#facet-item__row--"+facetname).slideToggle();
    l.parent().addClass('hide');
}

function load_facet_jobs(facet_url,facet_div) {
    window.facet_history = false;
    facet_url = facet_url ? facet_url : "";
    
    window.facet_loading = true;
    
    if(window.facet_history==true && window.history!=null && window.history.pushState!=null){
        window.history.pushState({},"",facet_url);
    }
    
    $.get(facet_url, function(data) {
        $(facet_div).html( $(data).find('.jobs-section').html() );
        window.facet_loading = false;
    });
}

// Function to load Similar Jobs within Job Details pages
function ajaxloadjobs(jobsurl,callback) {
    $.get(jobsurl, function(data) {
        $('.similar-jobs--job-js').html( $(data).find('.similar-jobs--jobs-search-js').html() );
        var similar_jobs_content = $(data).find('.similar-jobs--jobs-search-js').html();
        // check if similar_jobs_content is not empty
        if ($.trim(similar_jobs_content)) {
            $('.similar-jobs-element-js').each(function() {
                var similar_jobs_element_classes = $(this).attr('class');
                //var similar_jobs_element_classes_new = similar_jobs_element_classes.replaceAll('--has-similar-jobs-js','').replaceAll('hide','');
                var similar_jobs_element_classes_new = similar_jobs_element_classes.replace(/--has-similar-jobs-js/g,'').replace(/hide/g,'');
                $(this).attr('class',similar_jobs_element_classes_new);
            });
        }
        else {
            $('.similar-jobs-element-js').each(function() {
                var similar_jobs_element_classes = $(this).attr('class');
                //var similar_jobs_element_classes_new = similar_jobs_element_classes.replaceAll('--no-similar-jobs-js','');
                var similar_jobs_element_classes_new = similar_jobs_element_classes.replace(/--no-similar-jobs-js/g,'');
                $(this).attr('class',similar_jobs_element_classes_new);
            });
        }
        callback();
    });
}
function loadjob() {
    $('.job-details-preloader-js').addClass('hide');
    $('.job-details-inner-js').addClass('active');
}

$(document).ready(function() {
    top_offset_height = $('.header-outer').outerHeight() + 20;

    // Preloaders
    $('.preloader-wrapper').attr('style','top: '+$(window).scrollTop()+'px;');

    // Setting responsive videos
    setrespvideos();

    $('.jobs-section__paginate .prev_page').html('<img src="/system/production/assets/357052/original/pagination-prev.png">');
    $('.jobs-section__paginate .next_page').html('<img src="/system/production/assets/357051/original/pagination-next.png">');

    // Setting the Saved Jobs link
    var c_jobs_temp = localStorage.getItem('c_jobs') ? JSON.parse(localStorage.getItem('c_jobs')) : [];
    var saved_jobs_query;
    if (c_jobs_temp.length != 0) {
        saved_jobs_query = '/jobs/search?external_id[]='+c_jobs_temp.join('&external_id[]=')+'&saved_jobs=1';
        $('.saved_jobs_link').prop('href',saved_jobs_query);

        if (window.location.pathname == '/pages/saved-jobs') {
            window.location.replace(saved_jobs_query);
        }
    }

    $(window).resize(function(){
        // Screen section: set min-height same as window height
        $('.screen-section').css('min-height',$(window).height()+'px');

        // Home page
        if ($('.job-category__item').length > 1) {
            setHeight('.job-category__item-inner');
            setHeight('.job-category__item');
        }
        if ($('.diversity-column').length > 1) {
            setHeight('.diversity-column');    
        }
        if ($('.benefit-title-js').length > 1) {
            setHeight('.benefit-title-js');    
        }
        if ($('.benefit-content-js').length > 1) {
            setHeight('.benefit-content-js');    
        }

        // Content pages: set minimum height + set scrolling
        if ($(window).height() == $(document).height()) {
            $('body').addClass('no-scroll');
        }
        else {
            $('body').removeClass('no-scroll');
        }
        var constant_containers_height = $('.top-wrapper').outerHeight() + $('.footer').outerHeight();
        var template_content_min_height = $(window).height() - constant_containers_height;
        $('.template-content').attr('style','min-height: '+template_content_min_height+'px;');
        var total_content_height = constant_containers_height+template_content_min_height;

        // Content pages: same height featured items
        if ($('.page-details__featured-item').length > 1) {
            setHeight('.page-details__featured-list-image');
        }

        // Same height containers
        var same_height_counter = 0;
        var same_height_class_new = '';
        if ( $('.same-height-parent-js').length > 0 ) {
            $('.same-height-parent-js').each( function() {
                same_height_counter++;
                if ( $(this).find('.same-height-item-js').length > 0 ) {
                    $(this).find('.same-height-item-js').each( function() {
                        same_height_class_new = 'same-height-item--'+same_height_counter;
                        $(this).addClass(same_height_class_new);
                    });
                    setHeight('.'+same_height_class_new);
                }
            });
        }
    });

    // Mobile menu
    $('.header__menu-mobile-button').click(function() {
        if ( $('.header__menu.active').length > 0 ) {
            $('.header__menu-mobile-button a').attr('aria-expanded','false');
            $('.header__menu').attr('aria-hidden','true');
        }
        else {
            $('.header__menu-mobile-button a').attr('aria-expanded','true');
            $('.header__menu').attr('aria-hidden','false');
        }
        $('.header__menu').toggleClass('active');
    });

    // Keyword auto-fill
    $(document).on("click", ".cs_jsearchform .ui-autocomplete-foot a", function(e){
        window.location.href = "/search/jobs/?q="+$('#cs_jobsearchforminput_9ZQ7').val();
    });

    // Talent Network links
    $('.talent-network-link').click(function() {
        $('#talent-network-main')[0].click();
    });

    // Candidate Notifications
    /*$(document).on("click", ".candidate-notification-link", function(e){
        $('#candidateJobNotificationLauncher')[0].click();
    });*/
    $(document).on("click", ".candidate-notification-link", function(e){
        $('.tm_notification_link')[0].click();
    });

    // Home page: Search down button smooth scroll # links
    $(function() {
        $('.search-arrow a[href*="#"]:not([href="#"])').click(function() {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']')-100;
            $('html,body').animate({
                scrollTop: target.offset().top - top_offset_height
            }, 1000);
            return false;
        });
    });

    // Job Search Results page
    // Facet code 2
    // Show/hide facets
    $(document).on('click', '.facet-filter-results-button', function() {
        $('.facet-section').toggleClass('active');
    });
    // Expanding/collapsing Facet options
    $(document).on("click", ".facet-item__heading a", function(){ facet_expand_collapse($(this)); });
    // Ajax-ing Job Search Results
    $(document).on("click", ".facet-item__option-link", function(e){ ds_tm_facet_click(e); });
    // Showing more Facet options over the facet_num_limit
    $(document).on("click", ".facet-item__show-more", function(e){ ds_tm_facet_more_click(e); });
    // Render map
    if ($('.jobs-section__map.active').length > 0) {
        pinbackmap();
    }
    // Google Maps show/hide  
    $(document).on("click", "a.jobs-section__map-button", function() {
        google_map_counter = $('#google-map-counter').val();
        $('#google-map-counter').val(google_map_counter === "true" ? "false" : "true");

        $('.jobs-section__map').toggleClass('active');
        $('a.jobs-section__map-button').toggleClass('hide');
        if ($('.jobs-section__map.active').length > 0) {
            pinbackmap();
        }
    });
    // Google Maps scroll on/off
    $('.jobs-section__map iframe').addClass('scrolloff');
    $('.jobs-section__map').on('click', function () {
        $('.jobs-section__map iframe').removeClass('scrolloff');
    });
    $('.jobs-section__map iframe').mouseleave(function () {
        $('.jobs-section__map iframe').addClass('scrolloff');
    });

    // Job Details page
    // Back to Search Results button
    if ($('#back-to-search').length > 0) {
        if ( document.referrer.indexOf('/search') > -1 && document.referrer.indexOf('/jobs') > -1 && document.referrer != '' ) {
            $('#back-to-search').attr('href',document.referrer);
        }
    }
    // Bottom Apply button
    $('#apply-bottom').click(function() {
        $('#apply-top a')[0].click();
    });
    // Bottom Refer button
    $('.refer-bottom').click(function() {
        $('#refer-top a')[0].click();
    });
    // Share texts
    $('.cs_share_twitter_btn').append('<span class="show-for-sr">share to twitter</span>');
    $('.cs_facebook_btn').append('<span class="show-for-sr">share to facebook</span>');
    $('.cs_share_linkedin_btn').append('<span class="show-for-sr">share to linkedin</span>');
    // Social Referral
    $('a.social-share-url__copy-js').click(function() {
        var copiedtext = $(this).prev('input')[0];

        /* Select the text field */
        copiedtext.select();
        copiedtext.setSelectionRange(0, 99999); /* For mobile devices */

        /* Copy the text inside the text field */
        document.execCommand('copy');

        $(this).text('Copied!');
        setTimeout(function(){ $(this).text('Copy'); }, 3000);
    });

    $('.the-home-hero-slider').slick({
        dots: false,
        arrows: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: 4000,
        speed: 1000,
        fade: true,
        cssEase: 'linear',
        slidesToShow: 1,
        adaptiveHeight: false,
        centerMode: false,
    });
    $('.the-simple-slider').slick({
        dots: false,
        arrows: true,
        infinite: true,
        autoplay: true,
        autoplaySpeed: 3000,
        speed: 800,
        slidesToShow: 1,
        prevArrow:"<button type='button' class='slick-prev'><i class='fa fa-chevron-left' aria-hidden='true'></i></button>",
        nextArrow:"<button type='button' class='slick-next'><i class='fa fa-chevron-right' aria-hidden='true'></i></button>"
    });
    $(function() {     
        // $('html').click(function(e) {
        //     e.preventDefault();
        //     console.log("don't say it!!!");
        //     if ( $('.btn-more').hasClass('open-trigger') ) {
        //         $(this).removeClass('open-trigger');
        //         $(this).find('.fa').addClass('fa-caret-down');
        //         $(this).find('.fa').removeClass('fa-caret-up');
        //         $(".the-submenu").removeClass('show');
        //     }
        // });
        $('.btn-more, .btn-jobs-area').on('click',function(e) {
            e.preventDefault();
            console.log('click button');
            if ( $(this).hasClass('open-trigger') ) {
                $(this).removeClass('open-trigger');
                $(this).find('.fa').addClass('fa-caret-down');
                $(this).find('.fa').removeClass('fa-caret-up');
                $(this).next(".the-submenu").removeClass('show');
            }
            else {
                $(this).addClass('open-trigger');
                $(this).find('.fa').removeClass('fa-caret-down');
                $(this).find('.fa').addClass('fa-caret-up');
                $(this).next(".the-submenu").addClass('show');
            }
        });
        
    });
});

$(window).load(function() {
    $(window).resize();
});