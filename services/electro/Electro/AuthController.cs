using System;
using System.Collections.Concurrent;
using Electro.Model;
using Electro.Utils;

namespace Electro
{
	class AuthController
	{
		public User AddUser(string login, string pass)
		{
			var user = new User
			{
				Id = Guid.NewGuid(),
				Login = login,
				PasswordHash = CryptUtils.CalcHash(pass)
			};
			return users.TryAdd(login, user) ? user : null;
		}

		public User FindUser(string login, string pass = null)
		{
			User user;
			return users.TryGetValue(login, out user) && (pass == null || user.PasswordHash == CryptUtils.CalcHash(pass)) ? user : null;
		}

		ConcurrentDictionary<string, User> users = new ConcurrentDictionary<string, User>();
	}
}
