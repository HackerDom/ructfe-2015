using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using Electro.Model;
using Electro.Utils;
using log4net;

namespace Electro
{
	public class AuthController
	{
		private readonly StatePersister statePersister;

		public AuthController(IEnumerable<User> users, StatePersister statePersister)
		{
			LoadState(users);
			this.statePersister = statePersister;
		}

		private void LoadState(IEnumerable<User> users)
		{
			users.ForEach(user => AddUser(user));
			log.InfoFormat("Loaded users state. Now have {0} users", this.users.Count);
		}

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
			statePersister.SaveUser(user);
			return AddUser(user);
		}

		private User AddUser(User user)
		{
			if(user == null || user.Login == null)
				return null;
			return users.TryAdd(user.Login, user) ? user : null;
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

		private static readonly ILog log = LogManager.GetLogger(typeof(AuthController));
	}
}
