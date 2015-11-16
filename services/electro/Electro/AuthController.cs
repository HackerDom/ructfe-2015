using System;
using System.Collections.Concurrent;
using Electro.Model;
using Electro.Utils;

namespace Electro
{
	public class AuthController
	{
		public User AddUser(string login, string pass, string publicMessage, string privateNotes)
		{
			var user = new User
			{
				Id = Guid.NewGuid(),
				Login = login,
				PublicMessage = publicMessage,
				PrivateNotes = privateNotes,
				PasswordHash = CryptUtils.CalcHash(pass)
			};
			return users.TryAdd(login, user) ? user : null;
		}

		public User FindUserAuthorized(string login)
		{
			User user;
			return users.TryGetValue(login, out user) ? user : null;
		}

		public User FindUser(string login, string pass)
		{
			User user;
			return users.TryGetValue(login, out user) && user.PasswordHash == CryptUtils.CalcHash(pass) ? user : null;
		}

		ConcurrentDictionary<string, User> users = new ConcurrentDictionary<string, User>();
	}
}
