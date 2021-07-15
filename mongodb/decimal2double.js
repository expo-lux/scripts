var y = NumberDecimal(100.1);
print(y);
var x = y + "";
print(x);
var z = x.replace("NumberDecimal(\"", "");
z = z.replace("\")", "");
print(z);

var t = parseFloat(z);
t=t+1;
print(t);
