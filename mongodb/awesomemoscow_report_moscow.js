db.Event.aggregate(
[
{
  $match: { 
     "_header._created":  { $lte: new Date(), $gt: new Date(new Date()-7 * 60 * 60 * 24 * 1000) }
  }
},
{
  $lookup:  {
    from: "Class",
    localField: "ClassId",
    foreignField: "_id",
    as: "embeddedData"
    
  }
},
{
  $unwind: "$embeddedData"
},
{  
  $project : {
    Название_Класса: "$embeddedData.ClassName",
    Название_События:"$Name", 
    Место: { $ifNull: [ "$Place", "-" ] },
    Дата_создания: "$_header._created",
    Создано_на_основе_идеи: { 
      $cond : [{$not :"$SourceIdeaUrl"},"Нет", "Да"]
    },
    Идея: "$SourceIdeaUrl",
    _id: 0,
//    Описание:"$Description",
    Город: "$embeddedData.City.FORMALNAME",
    Количество_участников: { 
      $size : "$Participants"
    }
  }
},
//{$match: 
//  { "Город": {$ne :"Москва"} }
//}
{
  $match: {
     "Город": "Москва" 
  }
}
])