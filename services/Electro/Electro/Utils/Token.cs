using System;
using System.Runtime.Serialization;

namespace Electro.Utils
{
	[DataContract]
	internal class Token
	{
		[DataMember(Name = "login", Order = 1)] public string Login;
	}
}