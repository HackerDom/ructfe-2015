﻿using System;
using System.Runtime.Serialization;

namespace Electro.Utils
{
	[DataContract]
	internal class Token : JsonHelper<Token>
	{
		[DataMember(Name = "login", Order = 1)] public string Login;
		[DataMember(Name = "dt", Order = 2)] public DateTime DateTime;
	}
}