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
    ��������_������: "$embeddedData.ClassName",
    ��������_�������:"$Name", 
    �����: { $ifNull: [ "$Place", "-" ] },
    ����_��������: "$_header._created",
    �������_��_������_����: { 
      $cond : [{$not :"$SourceIdeaUrl"},"���", "��"]
    },
    ����: "$SourceIdeaUrl",
    _id: 0,
//    ��������:"$Description",
    �����: "$embeddedData.City.FORMALNAME",
    ����������_����������: { 
      $size : "$Participants"
    }
  }
},
//{$match: 
//  { "�����": {$ne :"������"} }
//}
{
  $match: {
     "�����": "������" 
  }
}
])