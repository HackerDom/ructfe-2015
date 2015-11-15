using System;
using System.IO;
using System.Runtime.Serialization.Json;
using System.Text;
using System.Xml;
using log4net;

namespace Electro.Utils
{
	public static class JsonHelper
	{
		public static T TryParseJson<T>(string record)
		{
			try { return ParseJson<T>(record); } catch(Exception) { return default(T); }
		}

		public static T ParseJson<T>(string record)
		{
			return ParseJson<T>(Encoding.UTF8.GetBytes(record));
		}

		public static T ParseJson<T>(byte[] record)
		{
			return ParseJson<T>(record, 0, record.Length);
		}

		public static T ParseJson<T>(byte[] record, int offset, int length)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(record, offset, length, XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T)).ReadObject(reader);
		}

		public static T ParseJson<T>(Stream stream)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(stream, XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T)).ReadObject(reader);
		}

		public static string ToJsonString<T>(this T obj, bool runtime = true)
		{
			return Encoding.UTF8.GetString(obj.ToJson(runtime));
		}

		public static byte[] ToJson<T>(this T obj, bool runtime = true)
		{
			using(var stream = new MemoryStream())
			{
				obj.ToJson(stream, runtime);
				return stream.ToArray();
			}
		}

		public static void ToJson<T>(this T obj, Stream stream, bool runtime = true)
		{
			using(var writer = JsonReaderWriterFactory.CreateJsonWriter(stream, Encoding.UTF8, false))
				new DataContractJsonSerializer(runtime ? obj.TryGetRuntimeType() : typeof(T)).WriteObject(writer, obj);
		}

		public static Type TryGetRuntimeType<T>(this T obj)
		{
			return Equals(obj, null) ? typeof(T) : obj.GetType();
		}

		private static readonly ILog log = LogManager.GetLogger(typeof(JsonHelper));
	}
}