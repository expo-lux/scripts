function dec2double(value) {
  	var x = value + "";
  	x = x.replace('NumberDecimal(\"', '');
  	x = x.replace('\")', '');
	return parseFloat(x);
}

use reformagkh;
var s;
s = "Address;min_floor_old;min_floor_new;max_floor_old;max_floor_new;resid_old;resid_new;nonresid_old;nonresid_new;common_old;common_new";
print(s);

db.GetHouseProfile988Response.find().snapshot().forEach(
  function (temp) {
    // update document, using its own properties
//   	print(temp.HouseDisplayAddress);
   	s = temp.HouseDisplayAddress + ";";
	value  = temp.house_profile_data.floor_count_min;
	s += temp.GisGkh.Info.MinFloorCount + ";";
//	print("floor min old:" + temp.GisGkh.Info.MinFloorCount);
	temp.GisGkh.Info.MinFloorCount = value;
	s += temp.GisGkh.Info.MinFloorCount + ";";
	//print("floor min new:" + value);
	
	value = temp.house_profile_data.floor_count_max;
	//print("floor max old:" + temp.GisGkh.Info.BasicCharacteristicts.FloorCount);
	s += temp.GisGkh.Info.BasicCharacteristicts.FloorCount + ";";
	temp.GisGkh.Info.BasicCharacteristicts.FloorCount = value;
	s += temp.GisGkh.Info.BasicCharacteristicts.FloorCount + ";";
	//print("floor max new:" + value);
	
	value = temp.house_profile_data.area_residential;
	//print("area residental old:" + temp.GisGkh.Info.ExtendedData.BuildArea.Resid);
	s += temp.GisGkh.Info.ExtendedData.BuildArea.Resid + ";";
	temp.GisGkh.Info.ExtendedData.BuildArea.Resid = dec2double(value);
	s += temp.GisGkh.Info.ExtendedData.BuildArea.Resid + ";";
	//print("area residental new:" + temp.GisGkh.Info.ExtendedData.BuildArea.Resid);
	
	value = temp.house_profile_data.area_non_residential;	
	//print("are non residental old:" + temp.GisGkh.Info.ExtendedData.BuildArea.NonResid);
	s += temp.GisGkh.Info.ExtendedData.BuildArea.NonResid + ";";
	temp.GisGkh.Info.ExtendedData.BuildArea.NonResid = dec2double(value);
	s += temp.GisGkh.Info.ExtendedData.BuildArea.NonResid + ";";
	//print("area non residental new:" + temp.GisGkh.Info.ExtendedData.BuildArea.NonResid);
	
	value = temp.house_profile_data.area_common_property;

//	print("area basement old:" + temp.GisGkh.Info.ExtendedData.BuildArea.Common);
	s += temp.GisGkh.Info.ExtendedData.BuildArea.Common + ";";
	temp.GisGkh.Info.ExtendedData.BuildArea.Common = dec2double(value);
	s += temp.GisGkh.Info.ExtendedData.BuildArea.Common + ";";
//	print("are basement new:" + temp.GisGkh.Info.ExtendedData.BuildArea.Common);
	
	print(s);
	db.GetHouseProfile988Response.save(temp); 
  }
)
  
