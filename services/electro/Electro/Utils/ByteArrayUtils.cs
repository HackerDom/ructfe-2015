using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Electro.Utils
{
	static class ByteArrayUtils
	{
		public static string ToHex(this byte[] bytes)
		{
			return bytes.ToHex(0, bytes.Length);
		}

		public static string ToHex(this byte[] bytes, int offset, int count)
		{
			if(bytes.Length < offset + count)
				throw new ArgumentOutOfRangeException();
			var array = new char[count << 1];
			for(int i = 0; i < count; i++)
			{
				var b = bytes[offset + i];
				var hb = b >> 4;
				array[i << 1] = (char)(hb > 9 ? hb + ByteA - 10 : hb + Byte0);
				var lb = b & 0xf;
				array[(i << 1) + 1] = (char)(lb > 9 ? lb + ByteA - 10 : lb + Byte0);
			}
			return new string(array);
		}

		public static byte[] ConvertFromHex(this string str)
		{
			var res = new byte[str.Length / 2];
			for(int i = 0; i < res.Length; i++)
				res[i] = Convert.ToByte(str.Substring(i * 2, 2), 16);
			return res;
		}

		public static bool TryConvertFromHex(this string str, out byte[] buff)
		{
			try
			{
				buff = ConvertFromHex(str);
				return true;
			}
			catch(Exception)
			{
				buff = null;
				return false;
			}
		}

		private const int Byte0 = '0';
		private const int ByteA = 'a';
	}
}
