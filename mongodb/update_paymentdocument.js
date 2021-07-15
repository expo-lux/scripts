статуса платежных документов за июль с 2 на 1 для адресов 40-летия Победы
// 0 не отправлен
// 1 отправлен
// 2 ошибка отправки
// 3 ожидает отправки
// 5 отозван
db.PaymentDocument.update(
	{
		
		"PublicationStatus": NumberInt(2),
		"AddressInfo.HouseDisplayAddress": /.*40-летия Победы.*/i,
		"MainInfo.Date.FilterValue": NumberInt(201707) 
	},
	{ 
		$set: 
			{
				"PublicationStatus": NumberInt(1),
			}
	},
	{
		upsert: false, multi: true
	}
)
