﻿using System;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;

namespace Electro.Crypto
{
	public static class HomoCrypto
	{
		public static BigInteger[] EncryptVector(int[] vector, PublicKey publicKey)
		{
			return vector.Select(i => Encrypt(i, publicKey)).ToArray();
		}

		public static BigInteger Encrypt(int val, PublicKey publicKey)
		{
			BigInteger core = 0;
			var r = RandomNumberGenerator.Create();
			byte[] randomBuff = new byte[1];
			for(int i = 0; i < publicKey.KeyParts.Length; i++)
			{
				r.GetBytes(randomBuff);
				if(i == 0 || randomBuff[0] % 2 == 1)
					core = core + publicKey.KeyParts[i];
			}
			r.GetNonZeroBytes(randomBuff);
			return core + (publicKey.MaxNum * randomBuff[0]) + val;
		}

		public static int[] DecryptVector(BigInteger[] vector, PrivateKey privateKey)
		{
			return vector.Select(bi => Decrypt(bi, privateKey)).ToArray();
		}

		public static int Decrypt(BigInteger val, PrivateKey privateKey)
		{
			var m = val % privateKey.Key;
			return (int) (m % privateKey.MaxNum);
		}
	}
}
