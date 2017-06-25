import std.stdio;
import std.variant;

class Field
{
	string key;
	TypeInfo type;
	Variant value;

	this(string key,TypeInfo type,Variant value)
	{
		this.key = key;
		this.type = type;
		this.value = value;
	}
}


TypeInfo fromSQLType(int type)
{
	switch(type){
		case 1:
			return typeid(int);
			break;
		case 2:
			return typeid(double);
			break;
		case 3:
			return typeid(bool);
			break;
		case 4:
		default:
			return typeid(string);
			break;
	}
}

class Cargo
{
	public Field[string] fields;

	void add(string key,TypeInfo type,Variant value)
	{
		fields[key] = new Field(key,type,value);
	}

	auto opDispatch(string name)()
	{
		return fields[name].value.peek!fields[name].type;
	}

	T get(T)(string name)
	{
		//if(fields[name].type == typeid(int))
		//	return *(fields[name].value.peek!int);
		//pragma(msg,T);
		return fields[name].value.get!T;
	}
}

void main()
{
	writeln("run");
	Cargo cargo = new Cargo();
	cargo.add("test1",fromSQLType(1),Variant(1024));
	//auto t1 = cargo.fields["test1"].value.get!(cargo.fields["test1"].type);
	//auto t1 = cargo.fields["test1"];
	//writeln(typeid(t1),typeid(*(t1.value.peek!(t1.type))));
	auto t1 = cargo.get!int("test1");
	writeln(typeid(t1),t1);
}
