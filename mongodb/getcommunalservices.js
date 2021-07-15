use reformagkh;
var MyCursor = db.GetHouseProfile988Response.find({
    "full_address.street_formal_name": "Кыштымская"
}).snapshot();
print(MyCursor.count());
while (MyCursor.hasNext()) {
    house = MyCursor.next();
    var services = [];
    s = house.HouseDisplayAddress + ";";
    house.house_profile_data.communal_services.forEach(function(service) {
        //print(service.type)
        i = Number(service.type)
        //print(i)
        //print(service.filling_fact)
        services[i] = service.filling_fact
    })
    for (var i = 1; i <= 6; i++) {
	//filling_fact = 2 не предоставляется нет 0
    //filling_fact = 1 предоставляется да 1
	    if (services[i] == 1) {
			s = s + "1;"
		} else if (services[i] == 2) {
		    s = s + "0;"	
		}
    }
    print(s)
}