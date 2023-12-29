// Click Events
$('.list-link').click(listByCategory)

// .list-link Handler Functions
// List By Category Function
async function listByCategory() {
    // This function will have cases based off of val of target's id
    const id = $(this).attr("id")
    // Array of id names for the other div sections
    const containerArr = ["flash-container", "table-container", "results-container", "owner-container"];
    // loop that hides unnecessary containers
    for (let container of containerArr) {
        $(`#${container}`).hide()
    }

    // List By Category Cases
    // Case: id equals owner
    if(id === 'owners') {
        try {
            // Try GET request to api
            const response = await axios.get('/api/owners');
            // owners variable should be an array populated with objects
            const owners = response.data.owners;
            // loop that appends modified li to the #type-list ul
            for (let owner of owners) {
                const li = 
                `<li
                class="list-group-item owner-link"
                data-owner-id=${owner['id']}>
                ${owner['full_name']}</li>`;

                $("#type-list").append(li);
            }
        }
        catch (err) {
            console.log(err)
        }
    }

    // Case: id equals properties
    if(id === 'properties') {
        try {
            // Try GET request to api
            const response = await axios.get('/api/properties');
            // owners variable should be an array populated with objects
            const properties = response.data.properties;
            // loop that appends modified li to the #type-list ul
            for (let property of properties) {
                const li = 
                `<li
                class="list-group-item owner-link"
                data-owner-id=${property['owner_id']}>
                ${property['address']}</li>`;

                $("#type-list").append(li);
            }
        }
        catch (err) {
            console.log(err)
        }
    }

    // Case: id equals companies
    if(id === 'companies') {
        try {
            // Try GET request to api
            const response = await axios.get('/api/companies');
            // owners variable should be an array populated with objects
            const companies = response.data.companies;
            // loop that appends modified li to the #type-list ul
            for (let company of companies) {
                const li = 
                `<li
                class="list-group-item owner-link"
                data-owner-id=${company['owner_id']}>
                ${company['llc_name']}</li>`;

                $("#type-list").append(li);
            }
        }
        catch (err) {
            console.log(err)
        }
    }

    // Show Paginated List Section
    $("#list-container").show();
}

// Class Click Events
// .owner-link Click Event
$(document).on('click', '.owner-link', showOwnerData);

// .owner-link Handler Function
async function showOwnerData() {
    try{
        console.log('Show Owner Data: ')
    }
    catch (err) {
        console.log(err);
    }
}