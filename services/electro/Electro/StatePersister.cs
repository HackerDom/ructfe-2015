using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Electro.Crypto;
using Electro.Model;
using Electro.Utils;

namespace Electro
{
	public class StatePersister
	{
		private StreamWriter usersWriter;
		private StreamWriter keysWriter;

		private static readonly string usersFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "state/users");
		private static readonly string electionsFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "state/elections");
		private static readonly string keysFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "state/keys");

		public StatePersister()
		{
			Directory.CreateDirectory(Path.GetDirectoryName(usersFilePath));
		}

		public static IEnumerable<User> LoadUsers()
		{
			if(!File.Exists(usersFilePath))
				return new User[0];
			return File.ReadLines(usersFilePath).Select(s =>
			{
				try
				{
					return JsonHelper.ParseJson<User>(s);
				}
				catch(Exception)
				{
					return null;
				}
			}).Where(user => user != null);
		}

		public static IEnumerable<Election> LoadElections()
		{
			if(!File.Exists(electionsFilePath))
				return new Election[0];
			return File.ReadLines(electionsFilePath).Select(s =>
			{
				try
				{
					return JsonHelper.ParseJson<Election>(s);
				}
				catch(Exception)
				{
					return null;
				}
			}).Where(election => election != null);
		}

		public static IEnumerable<KeyValuePair<Guid, PrivateKey>> LoadKeys()
		{
			if(!File.Exists(keysFilePath))
				return new KeyValuePair<Guid, PrivateKey>[0];
			return File.ReadLines(keysFilePath).Select(s =>
			{
				try
				{
					return JsonHelper.ParseJson<KeyValuePair<Guid, PrivateKey>>(s);
				}
				catch(Exception)
				{
					return default(KeyValuePair<Guid, PrivateKey>);
				}
				
			}).Where(kvp => kvp.Value != null);
		}

		public void SaveUser(User user)
		{
			if(usersWriter == null)
			{
				lock(usersFilePath)
				{
					if(usersWriter == null)
						usersWriter = new StreamWriter(new FileStream(usersFilePath, FileMode.Append)) {AutoFlush = true};
				}
			}
			usersWriter.WriteLine(user.ToJsonString());
		}

		public static void SaveAllElections(IEnumerable<Election> elections)
		{
			using(var sw = new StreamWriter(electionsFilePath) { AutoFlush = true })
			{
				elections.Select(election => election.ToJsonString()).ForEach(sw.WriteLine);
			}
		}

		public void SaveKey(Guid electionId, PrivateKey privateKey)
		{
			if(keysWriter == null)
			{
				lock(keysFilePath)
				{
					if(keysWriter == null)
						keysWriter = new StreamWriter(new FileStream(keysFilePath, FileMode.Append)) { AutoFlush = true };
				}
			}

			keysWriter.WriteLine(new KeyValuePair<Guid, PrivateKey>(electionId, privateKey).ToJsonString());
		}
	}
}
