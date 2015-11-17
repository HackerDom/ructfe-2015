using System;
using System.Collections.Generic;
using System.Net;
using System.Runtime.Serialization;
using Electro.Model;
using Electro.Utils;

namespace ElectroChecker
{
	[DataContract]
	class IdState1
	{
		[DataMember] private string electionStartDate;
		[IgnoreDataMember] public DateTime ElectionStartDate;

		[DataMember] public Guid ElectionId;
		[DataMember] public User[] Candidates;
		[DataMember] public User[] Voters;
		[DataMember] public int[] expectedResult;

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			electionStartDate = ElectionStartDate.ToSortable();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			ElectionStartDate = DateTimeUtils.TryParseSortable(electionStartDate);
		}
	}

	[DataContract]
	class User
	{
		[DataMember] public string Login;
		[DataMember] public string Pass;
		[DataMember] public string PublicMessage;
		[DataMember] public string PrivateMessage;
		[DataMember] private Tuple<string,string,string,string>[] cookies;
		[IgnoreDataMember] public CookieCollection Cookies;

		[OnSerializing]
		private void OnSerializing(StreamingContext context)
		{
			var tmp = new List<Tuple<string, string, string, string>>();
			foreach(Cookie cookie in Cookies)
			{
				tmp.Add(new Tuple<string, string, string, string>(cookie.Name, cookie.Value, cookie.Path, cookie.Domain));
			}
			cookies = tmp.ToArray();
		}

		[OnDeserialized]
		private void OnDeserialized(StreamingContext context)
		{
			Cookies = new CookieCollection();
			foreach(var tuple in cookies)
			{
				Cookies.Add(new Cookie(tuple.Item1, tuple.Item2, tuple.Item3, tuple.Item4));
			}
		}
	}
}