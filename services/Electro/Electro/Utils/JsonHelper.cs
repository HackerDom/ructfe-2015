using System;
using System.IO;
using System.Runtime.Serialization.Json;
using System.Text;
using System.Xml;

namespace Electro.Utils
{
	[Serializable]
	public class JsonHelper<T> where T : class
	{
		public static T ParseJson(string record)
		{
			var reader = JsonReaderWriterFactory.CreateJsonReader(Encoding.UTF8.GetBytes(record), XmlDictionaryReaderQuotas.Max);
			return (T)new DataContractJsonSerializer(typeof(T)).ReadObject(reader);
		}

		public string ToJsonString()
		{
			return Encoding.UTF8.GetString(ToJson());
		}

		public byte[] ToJson()
		{
			using(var stream = new MemoryStream())
			{
				ToJson(stream);
				return stream.ToArray();
			}
		}

		public void ToJson(Stream stream)
		{
			using(var writer = JsonReaderWriterFactory.CreateJsonWriter(stream, Encoding.UTF8, false))
				new DataContractJsonSerializer(typeof(T)).WriteObject(writer, this);
		}

		private static readonly object NullObject = new object();
	}
}