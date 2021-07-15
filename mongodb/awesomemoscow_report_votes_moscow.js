db.Vote.aggregate(
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
  $unwind: {
    path: "$embeddedData",
    preserveNullAndEmptyArrays: true
  }
},
{  
  $project : {
    Название_Класса: { $ifNull: ["$embeddedData.ClassName", "-"] },
    Название_Голосования:"$VoteName", 
    Дата_создания: "$_header._created",
    Создано_на_основе_идеи: { 
      $cond : [{$not :"$SourceIdeaUrl"},"Нет", "Да"]
    },
    _id: 0,
    Город: "$embeddedData.City.FORMALNAME",
    Количество_участников: {$size : { "$ifNull": [ "$Users", [] ] }}
  }
},
{
  $match: {
     "Город": "Москва" 
  }
}
])