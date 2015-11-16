using System;
using System.Globalization;

namespace Electro.Utils
{
	public static class DateTimeUtils
	{
		public static DateTime TruncSeconds(this DateTime dateTime)
		{
			return dateTime.AddTicks(-dateTime.Ticks % 600000000);
		}

		public static DateTime TryParseSortable(string value)
		{
			DateTime dt;
			return DateTime.TryParseExact(value, "s", CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out dt) ? dt : DateTime.MinValue;
		}

		public static string ToSortable(this DateTime dateTime)
		{
			return dateTime.ToString("s");
		}

		public static long ToUnixTime(this DateTime dateTime)
		{
			return (long)(dateTime - UnixEpoch).TotalMilliseconds;
		}

		public static DateTime ParseUnixTime(long milliseconds)
		{
			return UnixEpoch + TimeSpan.FromMilliseconds(milliseconds);
		}

		public static int ToShortUnixTime(this DateTime dateTime)
		{
			return (int)(dateTime - UnixEpoch).TotalSeconds;
		}

		private static readonly DateTime UnixEpoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
	}
}