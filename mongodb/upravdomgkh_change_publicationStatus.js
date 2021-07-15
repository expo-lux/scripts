db.PaymentDocument.update(
   { "MainInfo.Date.Year": NumberInt(2018), "MainInfo.Date.Month": NumberInt(4), "PublicationStatus": NumberInt(3), "CompanyId": "73eba46a-0c6f-42d3-8a7b-2962f0fbf06d"},
   { $set: { PublicationStatus: 0} },
   { multi: true }
)