namespace Electro.Utils
{
	internal static class StringUtils
	{
		public static string TrimToLower(this string value)
		{
			return string.IsNullOrWhiteSpace(value) ? null : value.Trim().ToLowerInvariant();
		}

		public static string TrimToNull(this string value, params char[] chars)
		{
			if(value == null)
				return null;
			var result = value.Trim(chars);
			return result == string.Empty ? null : result;
		}
	}
}