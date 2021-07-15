//Во всех платежных документах за июль в разделе начисления в каждой жилищной услуге
// в поле объем услуги (если есть такое поле) поставить 0.0
var MyCursor = db.PaymentDocument.find({ "MainInfo.Date.FilterValue": NumberInt(201707)}).snapshot();
print(MyCursor.count());
while(MyCursor.hasNext()){
    obj = MyCursor.next();
    print(obj.AddressInfo.HouseDisplayAddress);
	var services = obj.ChargeInfo.HousingService;
	for(var i = 0; i < services.length; ++i) { 
	  if (typeof services[i].CommonVolume != "undefined") 	{
//	    print(services[i].CommonVolume + " " +services[i].ServiceType.Name)
	    services[i].CommonVolume = 0.0;
	  }
	}
	db.PaymentDocument.save(obj);
}
