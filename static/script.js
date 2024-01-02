// Site Set Up
// Global Value determines if user has used the search form since last page refresh.
const hasSearched = localStorage.getItem("searched");

if (hasSearched) {
    // unused containers
    const containerArr = ['list-container', 'table-container', 'owner-container'];
    // loop hiding containers
    for(let container of containerArr) {
        $(`#${container}`).hide();
    }
    // remove searched from localstorage
    localStorage.clear() 
} else {
    const containerArr = ['list-container', 'owner-container', 'results-container'];
    // loop hiding containers
    for(let container of containerArr) {
        $(`#${container}`).hide();
    }
}


// Click Events for Static Elements
$("#search-btn").click(setSearched);
$('.list-link').click(listByCategory);

// Click Events for Dynamic Elements
$(document).on('click', '.page-nav-btn', navTypePage);
$(document).on('click', '.owner-link', showOwnerData);


// Helper Functions
// Render Nav Buttons for Paginated Results
function renderNavButtons(category, navObj) {
    // Extract prev & next vals
    const prev = navObj["prev_page"];
    const next = navObj["next_page"];
    // Create Button Helper Function
    function createBtn(page_id, text) {
        // Create Dynamic page var
        const page = `${page_id}`;
        // Construct Button with url saved as data attribute
        // Use text parameter to give btn text
        const btn = 
        `<span 
        class="page-nav-btn ${category}-list"
        data-page-id="${page}">
        ${text}</span>`;
        // Add btn to container
        $("#nav-btn-container").append(btn);

    };
    // Case: prev is truthy
    if (prev) {createBtn(prev, 'prev')};
    // Case: next is truthy
    if(next) {createBtn(next, 'next')};
}

// Render Owner lis with links to owners and links to adjacent pages
async function renderAllOwnersByPage(page) {
    // Construct Dynmic URL path based on page parameter.
    const urlPath = `api/owners/${page}`;
    // Make GET request to urlPath
    const response = await axios.get(urlPath);
    // owners variable should be an array populated with objects
    const owners = response.data.owners;
    const pageNav = response.data.page_nav;
    // loop that appends modified li to the #type-list ul
    for (let owner of owners) {
        const li = 
        `<li
        class="list-group-item owner-link"
        data-owner-id=${owner['id']}>
        ${owner['full_name']}</li>`;

        $("#type-list").append(li);
    }
    // Function can be found under Helper Functions
    renderNavButtons('owners', pageNav);
}

// Render Property lis with links to owners and links to adjacent pages
async function renderAllPropertiesByPage(page) {
    // Construct Dynmic URL path based on page parameter.
    const urlPath = `api/properties/${page}`;
    // Make GET request to urlPath
    const response = await axios.get(urlPath);
    // owners variable should be an array populated with objects
    const properties = response.data.properties;
    const pageNav = response.data.page_nav;
    // loop that appends modified li to the #type-list ul
    for (let property of properties) {
        const li = 
            `<li
            class="list-group-item owner-link"
            data-owner-id=${property['owner_id']}>
            ${property['address']}</li>`;

        $("#type-list").append(li);
    }
    // Function can be found under Helper Functions
    renderNavButtons('properties', pageNav);
}

// Render Company lis with links to owners and links to adjacent pages
async function renderAllCompaniesByPage(page) {
    // Construct Dynmic URL path based on page parameter.
    const urlPath = `api/companies/${page}`;
    // Make GET request to urlPath
    const response = await axios.get(urlPath);
    // owners variable should be an array populated with objects
    const companies = response.data.companies;
    const pageNav = response.data.page_nav;
    // loop that appends modified li to the #type-list ul
    for (let company of companies) {
        const li = 
        `<li
        class="list-group-item owner-link"
        data-owner-id=${company['owner_id']}>
        ${company['llc_name']}</li>`;

        $("#type-list").append(li);
    }

    renderNavButtons("companies", pageNav);
}

// Handler Functions
// #search-btn Handler Function
function setSearched() {
    // searching with the form will add a truthy searched key to local storage.
    // the searched key will be cleared if the page ever loads with searched in localstorage.
    localStorage.setItem("searched", true);
}


// .list-link Handler Functions
async function listByCategory() {
    // This function will have cases based off of val of target's id
    const id = $(this).attr("id")
    // Array of id names for the other div sections
    const containerArr = ["flash-container", "table-container", "results-container", "owner-container"];
    // loop that hides unnecessary containers
    for (let container of containerArr) {
        $(`#${container}`).hide()
    }

    // Clear ul and nav-btn-container
    $("#type-list").empty();
    $("#nav-btn-container").empty();
    
    // Switch Statement determines what list rendering function is used based on target's id
    let renderFunc = undefined;
    switch(id) {
        case "owners":
            renderFunc = renderAllOwnersByPage;
            break;
        case "properties":
            renderFunc = renderAllPropertiesByPage;
            break;
        case "companies":
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

// Class Click Events


// .page-nav-btn Handler Function
function navTypePage() {
    try{
        // Get page id, model from data attributes
        const page = $(this).data("page-id");
        // Boolean variables determining which category is populating the type list section
        const isOwners = $(this).hasClass("owners-list");
        const isProperties = $(this).hasClass("properties-list");
        const isCompanies = $(this).hasClass("  companies-list");
        // Clear type list ul and nav btn container
        $("#type-list").empty();
        $("#nav-btn-container").empty();
        // Conditional determining which render function to use
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
        const containerArr = ["flash-container", "table-container", "results-container", "list-container"];
        // loop that hides unnecessary containers
        for (let container of containerArr) {
            $(`#${container}`).hide()
        }
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
            const li = `<li class="list-group-item">${property}</li>`;
            $("#property-list").append(li);
        };

        $("#owner-container").show();
    }
    catch (err) {
        console.log(err);
    }
}