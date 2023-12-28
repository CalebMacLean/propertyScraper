async function getOwnerInfo() {
    return await axios.get('/owner/11')
}
owner_info = getOwnerInfo()
console.log(owner_info)