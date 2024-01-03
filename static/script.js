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
        const table = $("<table></table>").addClass("table w-50 col-6");
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
            const tr = $("<tr></tr>");
            // populate tr w/ data as tds
            const nameTd = $("<td></td>")
            // adding owner-link
            .addClass("owner-link")
            .attr("data-owner-id", owner["id"])
            .text(owner.full_name);
            const propCountTd = $("<td></td>").addClass("text-center").text(owner.property_count);
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
    const pageBtnWrapper = $("<div></div>")
    .attr("id", "page-btn-wrapper")
    .addClass("d-flex flex-row justify-content-between mt-3")
    $listCon.append(pageBtnWrapper);

    // Int. Helper Functional
    function createBtn(pageId, text) {
        // create dynamic page var
        const page = `${pageId}`;
        // create btn element
        const btn = $("<button></button>")
        // classes for traversePages() and styles
        .addClass(`page-btn button btn-sm m-1`)
        .attr("id", `${text}-btn`)
        .attr("data-page-id", page)
        .attr("data-list-category", category)
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
    const uList = $("<ul></ul>").addClass('list-group w-50');
    // create/push to uList dynamic lis based on owner data
    for (let owner of owners) {
        const li = $("<li></li>")
        // bootstrap and showOwnerInfo() classes
        .addClass("list-group-item owner-link text-center")
        // showOwnerInfo() data-attr
        .attr("data-owner-id", owner["id"])
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
    const uList = $("<ul></ul>").addClass('list-group w-50');
    // create/push to uList dynamic lis based on owner data
    for (let property of properties) {
        const li = $("<li></li>")
        // bootstrap and showOwnerInfo() classes
        .addClass("list-group-item owner-link text-center")
        // showOwnerInfo() data-attr
        .attr("data-owner-id", property["owner_id"])
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
    const uList = $("<ul></ul>").addClass('list-group w-50');
    // create/push to uList dynamic lis based on owner data
    for (let company of companies) {
        const li = $("<li></li>")
        // bootstrap and showOwnerInfo() classes
        .addClass("list-group-item owner-link text-center")
        // showOwnerInfo() data-attr
        .attr("data-owner-id", company["owner_id"])
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
        const response = await axios.get(pathUrl);
        // JSON data variables
        const owners = response.data.owners;
        const properties = response.data.properties;
        const companies = response.data.companies;

        // render if results found in category
        if (owners || properties || companies) {
            // render owner results
            if (owners) {
                // create result wrapper
                const wrapper = $("<div></div>")
                .addClass("result-wrapper mr-2 ml-2")
                // create/push title
                const oTitle = $("<h4></h4>").text("Owners:");
                wrapper.append(oTitle);
                // create/populate list
                const oList = $("<ul></ul>").addClass("list-group");
                for (let owner of owners) {
                    const oLi = $("<li></li>")
                    // bootstrap and showOwnerInfo() class
                    .addClass("list-group-item owner-link")
                    // showOwnerInfo() data attribute
                    .attr("data-owner-id", owner["id"])
                    .text(owner["full_name"]);
                    // push li to ul
                    oList.append(oLi);
                }
                // push oList to wrapper
                wrapper.append(oList);
                // push wrapper to html
                $resultCon.append(wrapper);
            }

            // render property results
            if (properties) {
                // create result wrapper
                const wrapper = $("<div></div>")
                .addClass("result-wrapper mr-2 ml-2")
                // create/push title
                const pTitle = $("<h4></h4>").text("Properties:");
                wrapper.append(pTitle);
                // create/populate list
                const pList = $("<ul></ul>").addClass("list-group");
                for (let property of properties) {
                    const pLi = $("<li></li>")
                    // bootstrap and showOwnerInfo() class
                    .addClass("list-group-item owner-link")
                    // showOwnerInfo() data attribute
                    .attr("data-owner-id", property["owner_id"])
                    .text(property["address"]);
                    // push li to ul
                    pList.append(pLi);
                }
                // push oList to wrapper
                wrapper.append(pList);
                // push wrapper to html
                $resultCon.append(wrapper);
            }

            // render company results
            if (companies) {
                // create result wrapper
                const wrapper = $("<div></div>")
                .addClass("result-wrapper mr-2 ml-2")
                // create/push title
                const cTitle = $("<h4></h4>").text("Companies:");
                wrapper.append(cTitle);
                // create/populate list
                const cList = $("<ul></ul>").addClass("list-group");
                for (let company of companies) {
                    const cLi = $("<li></li>")
                    // bootstrap and showOwnerInfo() class
                    .addClass("list-group-item owner-link")
                    // showOwnerInfo() data attribute
                    .attr("data-owner-id", company["owner_id"])
                    .text(company["llc_name"]);
                    // push li to ul
                    cList.append(cLi);
                }
                // push oList to wrapper
                wrapper.append(cList);
                // push wrapper to html
                $resultCon.append(wrapper);
            }
        } else {
            const msg = $("<h4></h4>").text("No Results...");
            $resultCon.append(msg);
        }

        // show $resultCon
        $resultCon.show();
    }
    // log errors to console
    catch(err) {
        console.log(err);
    }
    $("#search-input").val("");
};

// Dynamic .page-btn Click Event
$(document).on('click', '#prev-btn', evt => traversePages(evt));
$(document).on('click', '#next-btn', evt => traversePages(evt));

// .page-btn Handler Function
function traversePages(evt) {
    // Uses renderAll____ByPages() to get prev or next paginated results
    evt.preventDefault();
    const $this = $(evt.target);
    // data attribute var
    const page = $this.attr("data-page-id");
    const category = $this.attr("data-list-category");
    // clear container
    $listCon.empty();
    try {
        // determine render func by switch statement
        switch (category) {
            case "owners":
                renderAllOwnersByPage(page);
                break;
            case "properties":
                renderAllPropertiesByPage(page);
                break;
            case "companies":
                renderAllCompaniesByPage(page);
                break;
            default:
                $listCon.append($("<h4>Something Went Wrong...</h4>"));
        }
    }
    // log errors to console
    catch(err) {
        console.log(err);
    }
};

// Dynamic .owner-link Click Event
$(document).on("click", ".owner-link", evt => showOwnerInfo(evt));

// .owner-link Handler Function
async function showOwnerInfo(evt) {
    // uses owner-id data attribute to make request to /api/owners/<owner_id>
    // hide/clear sections
    hideSections();
    // try api request / catch errors and log to console
    try {
        // get owner data from api with owner id found in target's data attribute
        const target = $(evt.target);
        const ownerId = target.attr("data-owner-id");
        const urlPath = `/api/owner/${ownerId}`;
        const response = await axios.get(urlPath);
        const owner = response.data.owner;

        // make top of section
        const top = $("<div></div>").addClass("row d-flex flex-column justify-content-start");
        const title = $("<h1></h1>").text(owner["full_name"]);
        top.append(title);
        // <p> factory with unique text vals, determines if owner has a company
        let max = undefined;
        owner["llc_name"] ? max = 3 : max = 2;
        for (let i = 0; i < max; i++) {
            let txt = undefined;
            switch (i) {
                case 0:
                    txt = `Mailing Address: ${owner["address"]}`;
                    break;
                case 1:
                    txt = `Property Count: ${owner["property_count"]}`;
                    break;
                case 2:
                    txt = `Company Name: ${owner["llc_name"]}`;
                    break;
            }
            const p = $("<p></p>").text(txt);
            top.append(p);
        }
        // push top into section
        $ownerCon.append(top);

        // make bottom of section
        const bottom = $("<div></div>").addClass("row d-flex flex-column justify-content-start");
        const subTitle = $("<h4></h4>").text("Properties")
        bottom.append(subTitle);
        const propList = $("<ul></ul>").addClass("list-group");
        // <li> factory with unique addresses
        for (let property of owner["properties"]) {
            const li = $("<li></li>")
            .addClass("list-group-item")
            .text(property);
            
            propList.append(li);
        }
        // push populated list into bottom
        bottom.append(propList);
        // push bottom into secction
        $ownerCon.append(bottom);

        // show section
        $ownerCon.show();
    }
    catch(err) {
        console.log(err);
    }
};
