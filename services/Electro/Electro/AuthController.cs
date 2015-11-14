using System;
using System.Collections.Concurrent;
using Electro.Model;
using Electro.Utils;

namespace Electro
{
	class AuthController
	{
		public bool AddUser(string login, string pass)
		{
			var user = new User
			{
				Id = Guid.NewGuid(),
				Login = login,
				Hash = CryptUtils.CalcHash(pass)
			};
			return users.TryAdd(login, user);
		}

		public User FindUser(string login, string pass)
		{
			var passHash = CryptUtils.CalcHash(pass);
			User user;
			return users.TryGetValue(login, out user) && user.Hash == passHash ? user : null;
		}

		ConcurrentDictionary<string, User> users = new ConcurrentDictionary<string, User>();
	}
}
