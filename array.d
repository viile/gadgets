module helpers.array;

import std.stdio;
import std.array;
import std.algorithm;

T array_shift(T)(ref T[] arr)
{
	if(!arr.length)
	{
		return T.init;
	}
	if(arr.length == 1)
	{
		auto v = arr[0];
		arr = [];
		return v;
	}
	else
	{
		auto v = arr[0];
		arr = arr[1 .. $];
		return v;
	}
}

T array_pop(T)(ref T[] arr)
{
	if(!arr.length)
	{
		return T.init;
	}
	if(arr.length == 1)
	{
		auto v = arr[$ - 1];
		arr = [];
		return v;
	}
	else
	{
		auto v = arr[$ - 1];
		arr = arr[0 .. $ - 1];
		return v;
	}
}
