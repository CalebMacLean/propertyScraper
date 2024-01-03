// Global jQuery Variables
const $tableCon = $("#table-container");
const $listCon = $("#list-container");
const $resultCon = $("#result-container");
const $ownerCon = $("#owner-container");

// Universal Helper Functions
// Hide Sections
function hideSections() {
    /*
    Accepts an array of jQuery obj and uses hide() to turn off there display and empty() to clear their children
    Parameters:
    - arr (array) : array of element obj
    */
    const containers = [$tableCon, $listCon, $resultCon, $ownerCon];
    for(let container of containers) {
        container.hide();
        container.empty()
    }
};

// Site Initiation
$(document).ready(generateTable());

// .navbar-brand Click Event
$(".navbar-brand").click(generateTable);

// site-initiation and .navbar-brand Handler Function
async function generateTable() {
    // Trys a GET request to /api/owners/most and creates a table from the response
    try{
        // hide/clear sections
        hideSections();
        // make GET request to API for top 10 property owners
        const response = await axios.get('/api/owners/most');
        const owners = response.data.owners;
        // create/push title
        const title = $("<h4></h4>").text("Owners With The Most Property");
        $tableCon.append(title);
        // create top of table
        const table = $("<table></table>").addClass("table w-50 col");
        const thead = $("<thead></thead>").addClass("thead-dark");
        const colRow = $("<tr></tr>");
        // create 3 unique th with name for column
        for(let i = 0; i < 2; i++) {
            // switch case determines text of th
            let txt = undefined;
            switch (i) {
                case 0:
                    txt = "Name";
                    break;
                case 1:
                    txt = "Property Count";
                    break;
            }
            // create and push th
            const th = $("<th></th>").attr("scope", "col").text(txt);
            colRow.append(th);
        }
        // push top of table
        thead.append(colRow);
        table.append(thead);
        // create bottom of table
        const tbody = $("<tbody></tbody>");
        // create dynamic tr with each owner in owners
        for(let owner of owners) {
            // data-owner-id and .owner-link needed for showOwnerInfo
            const tr = $("<tr></tr>").data("owner-id", owner.id).addClass("owner-link");
            // populate tr w/ data as tds
            const nameTd = $("<td></td>").text(owner.full_name);
            const propCountTd = $("<td></td>").text(owner.property_count);
            tr.append(nameTd, propCountTd);
            // push tr to tbody
            tbody.append(tr);
        }
        // push tbody
        table.append(tbody);
        // push table to html
        $tableCon.append(table);
        // show #table-container
        $tableCon.show();
    }
    catch(err) {
        console.log(err);
    }
};


// .nav-link Click Event
$(".nav-link").click(renderListContainer);

// renderListContainer Helper Function
function renderNavButtons(category, pageNav) {
    /*
    Renders page navigation buttons for paginated results
    Parameters:
    - category (str) : specifies owners, properties, or companies
    - pageNavObj (obj) : obj that has the pagination page data
    */
    // store pageNav attributes as variables
    const prev = pageNav["prev_page"];
    const next = pageNav["next_page"];

    // create wrapper for .page-btn elements and push onto html
    const pageBtnWrapper = $("<div></div>").attr("id", "page-btn-wrapper")
    $listCon.append(pageBtnWrapper);

    // Int. Helper Functional
    function createBtn(pageId, text) {
        // create dynamic page var
        const page = `${pageId}`;
        // create btn element
        const btn = $("<button></button>")
        // classes for traversePages() and styles
        .addClass(`btn btn-sm page-btn ${category}-list`)
        .data("page-id", page)
        .text(text);
        // push btn to markup
        $("#page-btn-wrapper").append(btn);
    }

    // Case: prev is truthy
    if (prev) {createBtn(prev, 'prev')};
    // Case: next is truty
    if (next) {createBtn(next, 'next')};
};

// renderListContainer() & traversePage() Helper Function
async function renderAllOwnersByPage(page) {
    // Renders lis with dynamic owner data
    // create dynamic url with page parameter
    const urlPath =`/api/owners/${page}`;

    // make GET request to urlPath
    const response = await axios.get(urlPath);
    // store JSON data in like vars
    const owners = response.data.owners;
    const pageNav = response.data.page_nav;

    // create ul for owner li
    const uList = $("<ul></ul>").addClass('list-group');
    // create/push to uList dynamic lis based on owner data
    for (let owner of owners) {
        const li = $("<li></li>")
        // bootstrap and showOwnerInfo() classes
        .addClass("list-group-item owner-link")
        // showOwnerInfo() data-attr
        .data("owner-id", owner["id"])
        .text(owner["full_name"]);
        // push li to uList
        uList.append(li);
    }
    // push uList to html
    $listCon.append(uList);
    renderNavButtons('owners', pageNav);
};

// renderListContainer() & traversePage() Helper Function
async function renderAllPropertiesByPage(page) {
    // Renders lis with dynamic property data
    // create dynamic url with page parameter
    const urlPath =`/api/properties/${page}`;

    // make GET request to urlPath
    const response = await axios.get(urlPath);
    // store JSON data in like vars
    const properties = response.data.properties;
    const pageNav = response.data.page_nav;

    // create ul for owner li
    const uList = $("<ul></ul>").addClass('list-group');
    // create/push to uList dynamic lis based on owner data
    for (let property of properties) {
        const li = $("<li></li>")
        // bootstrap and showOwnerInfo() classes
        .addClass("list-group-item owner-link")
        // showOwnerInfo() data-attr
        .data("owner-id", property["owner_id"])
        .text(property["address"]);
        // push li to uList
        uList.append(li);
    }
    // push uList to html
    $listCon.append(uList);
    renderNavButtons('properties', pageNav);
}

// renderListContainer() & traversePage() Helper Function
async function renderAllCompaniesByPage(page) {
    // Renders lis with dynamic company data
    // create dynamic url with page parameter
    const urlPath =`/api/companies/${page}`;

    // make GET request to urlPath
    const response = await axios.get(urlPath);
    // store JSON data in like vars
    const companies = response.data.companies;
    const pageNav = response.data.page_nav;

    // create ul for owner li
    const uList = $("<ul></ul>").addClass('list-group');
    // create/push to uList dynamic lis based on owner data
    for (let company of companies) {
        const li = $("<li></li>")
        // bootstrap and showOwnerInfo() classes
        .addClass("list-group-item owner-link")
        // showOwnerInfo() data-attr
        .data("owner-id", company["owner_id"])
        .text(company["llc_name"]);
        // push li to uList
        uList.append(li);
    }
    // push uList to html
    $listCon.append(uList);
    renderNavButtons('companies', pageNav);
}

// .nav-link Handler Function
async function renderListContainer() {
    // hide/clear sections
    hideSections();

    // renders $listCon based on click target's text
    const txtVal = $(this).text();
    // switch statement determines what render func to use
    let renderFunc = undefined;
    switch(txtVal) {
        case "Owners":
            renderFunc = renderAllOwnersByPage;
            break;
        case "Properties":
            renderFunc = renderAllPropertiesByPage;
            break;
        case "Companies":
            renderFunc = renderAllCompaniesByPage;
            break;
        default:
            renderFunc = renderNoResults;
    }

    // try renderFunc and show container
    try {
        renderFunc(1);
        $listCon.show();
    }
    catch(err) {
        console.log(err);
    }
};

// #search-btn Click Event
$("#search-btn").click(search);

// ##############################################
// Start Here
// ##############################################
// #search-btn Handler Function
async function search(evt) {
    // prevent default button behavior
    evt.preventDefault();
    // hide/clear sections
    hideSections();
    
    // try API interaction w/ search val
    try {
        const searchVal = $("#search-input").val();
        const pathUrl = `/api/search?query=${encodeURIComponent(searchVal.toUpperCase())}`;
        console.log(pathUrl)
        const response = await axios.get(pathUrl);
        // JSON data variables
        const owners = response.data.owners;
        const properties = response.data.properties;
        const companies = response.data.companies;

        // render if results found in category
        if (owners || properties || companies) {
            // render owner results
            if (owners) {
                // create/push title
                const oTitle = $("<h4></h4>").text("Owners:");
                $resultCon.append(oTitle);
                // create/populate list
                const oList = $("<ul></ul>").addClass("list-group");
                for (let owner of owners) {
                    const oLi = $("<li></li>")
                    // bootstrap and showOwnerInfo() class
                    .addClass("list-group-item owner-link")
                    // showOwnerInfo() data attribute
                    .data("owner-id", owner["id"])
                    .text(owner["full_name"]);
                    // push li to ul
                    oList.append(oLi);
                }
                // push oList to $resultCon
                $resultCon.append(oList);
            }

            // render property results
            if (properties) {
                // create/push title
                const pTitle = $("<h4></h4>").text("Properties:");
                $resultCon.append(pTitle);
                // create/populate list
                const pList = $("<ul></ul>").addClass("list-group");
                for (let property of properties) {
                    const pLi = $("<li></li>")
                    // bootstrap and showOwnerInfo() class
                    .addClass("list-group-item owner-link")
                    // showOwnerInfo() data attribute
                    .data("owner-id", property["owner_id"])
                    .text(property["full_name"]);
                    // push li to ul
                    pList.append(pLi);
                }
                // push oList to $resultCon
                $resultCon.append(pList);
            }

            // render company results
            if (companies) {
                // create/push title
                const cTitle = $("<h4></h4>").text("Companies:");
                $resultCon.append(cTitle);
                // create/populate list
                const cList = $("<ul></ul>").addClass("list-group");
                for (let company of companies) {
                    const cLi = $("<li></li>")
                    // bootstrap and showOwnerInfo() class
                    .addClass("list-group-item owner-link")
                    // showOwnerInfo() data attribute
                    .data("owner-id", company["owner_id"])
                    .text(owner["llc_name"]);
                    // push li to ul
                    cList.append(cLi);
                }
                // push oList to $resultCon
                $resultCon.append(cList);
            }
        } else {
            const msg = $("<h4></h4>").text("No Results...");
            $resultCon.append(msg);
        }

        // show $resultCon
        $resultCon.show();
    }
    catch(err) {
        console.log(err);
    }
    $("#search-input").val("");
};