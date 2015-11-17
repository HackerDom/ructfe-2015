using System;
using System.Collections.Generic;
using System.IO;

namespace ElectroChecker
{
	class UsersManager
	{
		static UsersManager()
		{
			names = File.ReadAllLines(namesPath);
			surnames = File.ReadAllLines(surnamesPath);
		}

		public static User GenUser(string name = null, string publicMessage = null, string privateNotes = null)
		{
			if(name == null)
				name = NextFullName();

			var login = name;
			string pass = Utils.GenRandomAlphaNumeric();
			if(publicMessage == null)
				publicMessage = "My public Message_" + Utils.GenRandomAlphaNumeric(10, 6);
			return new User { Login = login, Pass = pass, PublicMessage = publicMessage, PrivateMessage = privateNotes };
		}

		public static User GenRandomUser(string privateNotes = null)
		{
			return GenUser(null, null, privateNotes);
		}

		public static string NextFullName()
		{
			return names[random.Next(names.Length)] + "_" + surnames[random.Next(names.Length)] + "_" + Math.Abs(new object().GetHashCode());
		}

		static Random random = new Random();

		private static string[] names;
		private static string[] surnames;

		private const string namesPath = "static/names";
		private const string surnamesPath = "static/surnames";
	}
}
