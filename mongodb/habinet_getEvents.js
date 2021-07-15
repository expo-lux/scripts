use habinet;
db.Event.aggregate(
[{$lookup:
  {from: "Class",
    localField: "ClassId",
    foreignField: "_id",
    as: "embeddedData"
    
  }
},
{
  $unwind: "$embeddedData"
},
{ $project : 
  {
        Создан: "$_header._created",
    _id: 0,

    Название:"$Name", 
    Описание:"$Description",
    Место:"$Place",
    Название_Класса: "$embeddedData.ClassName",
    Город: "$embeddedData.City.FORMALNAME",
  }
}])