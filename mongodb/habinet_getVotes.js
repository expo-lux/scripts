use habinet;
db.Vote.aggregate(
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

    Голосование:"$VoteName", 
    Название_Класса: "$embeddedData.ClassName",
    Город: "$embeddedData.City.FORMALNAME",
  }
}])