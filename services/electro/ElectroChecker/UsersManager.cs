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

		public static User GenRandomUser(string privateMessage = null)
		{
			var login = UsersManager.NextFullName();
			string pass = Utils.GenRandomAlphaNumeric();
			string publicMessage = "My public Message_" + Utils.GenRandomAlphaNumeric(10, 6);
			return new User { Login = login, Pass = pass, PublicMessage = publicMessage, PrivateMessage = privateMessage};
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
