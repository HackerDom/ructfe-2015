using System;
using System.IO;
using System.Runtime.Serialization.Json;
using System.Text;
using System.Xml;

namespace Electro.Utils
{
	public static class JsonHelper
	{
		public static T ParseJson<T>(string record, bool useSimpleDictionaryFormat = false)
		{
			return ParseJson<T>(Encoding.UTF8.GetBytes(record), useSimpleDictionaryFormat);
		}

		public static T ParseJson<T>(byte[] record, bool useSimpleDictionaryFormat = false)
		{
			return ParseJson<T>(record, 0, record.Length, useSimpleDictionaryFormat);
		}

		public static T ParseJson<T>(byte[] record, int offset, int length, bool useSimpleDictionaryFormat = false)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(record, offset, length, XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T), useSimpleDictionaryFormat ? SimpleDictionarySettings : DefaultSettings).ReadObject(reader);
		}

		public static T ParseJson<T>(Stream stream)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(stream, XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T)).ReadObject(reader);
		}

		public static string ToJsonString<T>(this T obj, bool runtime = true, bool useSimpleDictionaryFormat = false)
		{
			return Encoding.UTF8.GetString(obj.ToJson(runtime, useSimpleDictionaryFormat));
		}

		public static byte[] ToJson<T>(this T obj, bool runtime = true, bool useSimpleDictionaryFormat = false)
		{
			using(var stream = new MemoryStream())
			{
				obj.ToJson(stream, runtime, useSimpleDictionaryFormat);
				return stream.ToArray();
			}
		}

		public static void ToJson<T>(this T obj, Stream stream, bool runtime = true, bool useSimpleDictionaryFormat = false)
		{
			using(var writer = JsonReaderWriterFactory.CreateJsonWriter(stream, Encoding.UTF8, false))
				new DataContractJsonSerializer(runtime ? obj.TryGetRuntimeType() : typeof(T), useSimpleDictionaryFormat ? SimpleDictionarySettings : DefaultSettings).WriteObject(writer, obj);
		}

		public static Type TryGetRuntimeType<T>(this T obj)
		{
			return Equals(obj, null) ? typeof(T) : obj.GetType();
		}

		private static readonly DataContractJsonSerializerSettings DefaultSettings = new DataContractJsonSerializerSettings();
		private static readonly DataContractJsonSerializerSettings SimpleDictionarySettings = new DataContractJsonSerializerSettings { UseSimpleDictionaryFormat = true };
	}
}