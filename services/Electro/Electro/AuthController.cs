using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using Electro.Model;

namespace Electro.Utils
{
	class AuthController
	{
		public bool AddUser(string name, string pass)
		{
			var user = new User
			{
				Id = Guid.NewGuid(),
				Name = name,
				Hash = CryptoUtils.CalcHash(pass)
			};
			return users.TryAdd(name, user);
		}

		public User FindUser(string name, string pass)
		{
			var passHash = CryptoUtils.CalcHash(pass);
			User user;
			return users.TryGetValue(name, out user) && user.Hash == passHash ? user : null;
		}

		ConcurrentDictionary<string, User> users = new ConcurrentDictionary<string, User>();
	}
}
