using System;
using System.IO;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using System.Text;

namespace Electro.Utils
{
	public static class TokenCrypt
	{
		static TokenCrypt()
		{
			try
			{
				CryptKey = JsonHelper.ParseJson<AesKey>(File.ReadAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, KeyFile)).Trim());
			}
			catch(FileNotFoundException)
			{
				using(var aes = new AesManaged())
				{
					aes.GenerateKey();
					aes.GenerateIV();
					CryptKey = new AesKey { Key = aes.Key, IV = aes.IV };
					File.WriteAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, KeyFile), CryptKey.ToJsonString());
				}
			}
		}

		public static string Decrypt(string tokenString)
		{
			var tokenBytes = Convert.FromBase64String(tokenString);
			using(var crypt = new AesManaged())
			using(var decryptor = crypt.CreateDecryptor(CryptKey.Key, CryptKey.IV))
			{
				var bytes = decryptor.TransformFinalBlock(tokenBytes, 0, tokenBytes.Length);
				return Encoding.UTF8.GetString(bytes);
			}
		}

		public static string Encrypt(string tokenString)
		{
			var tokenBytes = Encoding.UTF8.GetBytes(tokenString);
			using(var crypt = new AesManaged())
			using(var encryptor = crypt.CreateEncryptor(CryptKey.Key, CryptKey.IV))
			{
				var bytes = encryptor.TransformFinalBlock(tokenBytes, 0, tokenBytes.Length);
				return Convert.ToBase64String(bytes);
			}
		}

		[DataContract]
		private class AesKey
		{
			[DataMember(Name = "k", Order = 1)] private string key;
			[DataMember(Name = "iv", Order = 2)] private string iv;

			[IgnoreDataMember] public byte[] Key;
			[IgnoreDataMember] public byte[] IV;

			[OnSerializing]
			private void OnSerializing(StreamingContext context)
			{
				key = Convert.ToBase64String(Key);
				iv = Convert.ToBase64String(IV);
			}

			[OnDeserialized]
			private void OnDeserialized(StreamingContext context)
			{
				Key = Convert.FromBase64String(key);
				IV = Convert.FromBase64String(iv);
			}
		}

		private static readonly string KeyFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "key");
		private static readonly AesKey CryptKey;
	}
}