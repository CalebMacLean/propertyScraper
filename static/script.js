// Site Set Up
$(document).ready(function(){
    hideSections(["table-container", "list-container", "results-container", "owner-container"]);
    generateTable();
});
// Click Events for Static Elements
$("#search-btn").click(search);
$('.nav-link').click(listByCategory);

// Click Events for Dynamic Elements
$(document).on('click', '.page-btn', traversePages);
$(document).on('click', '.owner-link', showOwnerData);


// Helper Functions
// Hide Sections
function hideSections(arr) {
    for(let container of arr) {
        $(`#${container}`).hide();
    }
}

// render nav buttons for paginated results
function renderNavButtons(category, navObj) {

    // extract prev & next vals
    const prev = navObj["prev_page"];
    const next = navObj["next_page"];

    // Helper Function
    function createBtn(page_id, text) {
        // create dynamic page var
        const page = `${page_id}`;
        // create btn 
        const btn =
        $("<btn></btn>")
        // classes for traversePages
        .addClass(`page-btn ${category}-list`)
        .data("page-id", page)
        .text(text);
        // push btn to markup
        $("#page-btn-container").append(btn);

    };

    // Case: prev is truthy
    if (prev) {createBtn(prev, 'prev')};
    // Case: next is truthy
    if(next) {createBtn(next, 'next')};
}


// render owner lis with links to owners and links to adjacent pages
async function renderAllOwnersByPage(page) {
    // construct dynmic URL path based on page parameter.
    const urlPath = `api/owners/${page}`;
    // make GET request to urlPath
    const response = await axios.get(urlPath);
    // owners var should be an array populated with obj
    const owners = response.data.owners;
    const pageNav = response.data.page_nav;
    // loop that appends modified li to the #type-list ul
    for (let owner of owners) {
        // create dynamic li
        const li =
        $("<li></li>")
        // bootstrap class and showOwnerInfo class
        .addClass("list-group-item owner-link")
        // data-owner-id needed for showOwnerInfo
        .data("owner-id", owner["id"])
        .text(owner["full_name"]);

        $("#type-list").append(li);
    }
    // function can be found under Helper Functions
    renderNavButtons('owners', pageNav);
}


// render property lis with links to owners and links to adjacent pages
async function renderAllPropertiesByPage(page) {
    // construct dynmic URL path based on page parameter.
    const urlPath = `api/properties/${page}`;
    // make GET request to urlPath
    const response = await axios.get(urlPath);
    // owners var should be an array populated with obj
    const properties = response.data.properties;
    const pageNav = response.data.page_nav;
    // loop that appends modified li to the #type-list ul
    for (let property of properties) {
        // create dynamic li
        const li = 
        $("<li></li>")
        // bootstrap class and showOwnerInfo class
        .addClass("list-group-item owner-link")
        // data-owner-id needed for showOwnerInfo
        .data("owner-id", property['owner_id'])
        .text(property["address"]);
        // push li to markup
        $("#type-list").append(li);
    }
    // function can be found under Helper Functions
    renderNavButtons('properties', pageNav);
}


// render company lis with links to owners and links to adjacent pages
async function renderAllCompaniesByPage(page) {
    // construct dynmic URL path based on page parameter.
    const urlPath = `api/companies/${page}`;
    // make GET request to urlPath
    const response = await axios.get(urlPath);
    // owners var should be an array populated with obj
    const companies = response.data.companies;
    const pageNav = response.data.page_nav;
    // loop that appends modified li to the #type-list ul
    for (let company of companies) {
        // create dynamic li
        const li = 
        $("<li></li>")
        // bootstrap class and showOwnerInfo class
        .addClass("list-group-item owner-link")
        // data-owner-id needed for showOwnerInfo
        .data("owner-id", company["owner_id"])
        .text(company["llc_name"]);
        // push li to markup
        $("#type-list").append(li);
    }

    renderNavButtons("companies", pageNav);
}

// Renders Search result sections by categories includes title as h4, 
function renderSearchResults(map, objArr) {
    // Owners : {"ownerId": }
}

// Handler Functions
// #search-btn Handler Function
async function search(evt) {
    // Prevent default button behavior
    evt.preventDefault();
    // Hide Sections
    hideSections(['list-container', 'table-container', 'owner-container']);
    // Store search val
    const searchVal = $("#search-input").val();
    // Try/Catch API interaction
    try {
        // Make GET request to API
        const response = await axios.get(`/api/?${searchVal}`);
        // Store Results in respective categories
        const owners = response.data.owners;
        const properties = response.data.properties;
        const companies = response.data.companies;
        // Conditional checking in there were any results found
        if (owners || properties || companies) {
            if (properties) {renderSearchResults('')}
        }
        else {

        }
    }
    catch(err) {
        console.log(err);
    }
}

// document.ready Handler Function
async function generateTable() {
    try{
        // request top 10 property owners from database
        const response = await axios.get('api/owners/most');
        const owners = response.data.owners;
        // loop through each owner from response and create tr with dynamic data
        for (let owner of owners) {
            // data-owner-id and .ownerlink are needed to make tr link to detailed owner info
            const tr = $("<tr></tr>").data("owner-id", owner.id).addClass("owner-link");
            const nameTd = $("<td></td>").text(owner.full_name);
            const propCountTd = $("<td></td>").text(owner.property_count);
            // append new elements to document.
            tr.append(nameTd, propCountTd);
            $("#owner-tbody").append(tr);
            // display #table-container
            $("#table-container").show();
        }
    }
    catch(err){
        console.log(err);
    }
}

// .list-link Handler Functions
async function listByCategory() {
    // This function will have cases based off of val of target's id
    const id = $(this).text();
    // hide irrelevant sections
    hideSections(["table-container", "results-container", "owner-container"]);

    // clear ul and page-btn-container
    $("#type-list").empty();
    $("#page-btn-container").empty();
    
    // switch statement determines what list rendering function is used based on target's id
    let renderFunc = undefined;
    switch(id) {
        case "Owners":
            renderFunc = renderAllOwnersByPage;
            break;
        case "Properties":
            renderFunc = renderAllPropertiesByPage;
            break;
        case "Companies":
            renderFunc = renderAllCompaniesByPage;
            break;
    }

    //Try/Catch statement that will prevent error from disrupting page. 
    try {
        renderFunc(1);
    }
    catch (err) {
        console.log(err);
    }

    // Show Paginated List Section
    $("#list-container").show();
}

// .page-btn Handler Function
function traversePages() {
    try{
        // page-btn contain page-ids for prev or next pages
        const page = $(this).data("page-id");
        // bool vars
        const isOwners = $(this).hasClass("owners-list");
        const isProperties = $(this).hasClass("properties-list");
        const isCompanies = $(this).hasClass("  companies-list");
        // clear #type-list ul and #page-btn-container
        $("#type-list").empty();
        $("#page-btn-container").empty();
        // determine render function based on bool var
        if (isOwners) {
            return renderAllOwnersByPage(page);
        }
        else if (isProperties) {
            return renderAllPropertiesByPage(page);
        }
        else if (isCompanies) {
            return renderAllCompaniesByPage(page);
        }
        else {
            console.log("navPage() unexpectedly failed");
        }
        
    }
    catch(err) {
        console.log(err);
    }
}

// .owner-link Handler Function
async function showOwnerData() {
    try{
        // get owner id
        const ownerId = $(this).data("owner-id");
        // make GET request to API
        const response = await axios.get(`/api/owners/${ownerId}`);
        // access owner data
        const ownerObj = response.data.owner;
        // clear other sections
        hideSections(["table-container", "results-container", "list-container"]);
        // {"owner" : {id, full_name, address, *llc_name, *property_count, *[properties]}}
        $("#owner-name-h1").text(`${ownerObj['full_name']}`);
        $("#owner-address-p").text(`Mailing Address: ${ownerObj['address']}`);
        $("#property-count-p").text(`Property Count: ${ownerObj["property_count"]}`);
        // Conditional to include or hide company affiliation
        if (ownerObj["llc_name"]) {
            $("#owner-company-p").text(`Company Name: ${ownerObj['llc_name']}`);
        } else {
            $("owner-company-p").hide();
        }
        // Loop creates lis of properties in ownerObj
        const propertyArr = ownerObj["properties"];
        for (let property of propertyArr) {
            const li =
            $("<li></li>")
            .addClass("list-group-item")
            .text(property);
            // const li = `<li class="list-group-item">${property}</li>`;
            $("#property-list").append(li);
        };

        $("#owner-container").show();
    }
    catch (err) {
        console.log(err);
    }
}