using System;
using System.Collections;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net;
using Electro.Utils;

namespace Electro.Handlers
{
	internal class StaticHandler : BaseHttpHandler
	{
		public StaticHandler(string prefix, string root) : base(prefix)
		{
			this.root = Path.GetFullPath(root);
			localPath = new Uri(prefix.Replace("+", "localhost").Replace("*", "localhost")).LocalPath;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			var fileInfo = GetFileInfo(context.Request.Url);
			if(fileInfo == null)
				throw new HttpException(HttpStatusCode.NotFound, string.Format("File for url {0} not found", context.Request.Url));

			var lastModified = fileInfo.LastWriteTimeUtc.TruncSeconds();
			context.Response.AddHeader("Date", DateTime.UtcNow.ToString("r"));

			var contentType = GetContentType(Path.GetExtension(fileInfo.FullName));

			context.Response.AddHeader("Cache-Control", "max-age=" + MaxAge);
			context.Response.AddHeader("Last-Modified", lastModified.ToString("r"));
			context.Response.AddHeader("Accept-Ranges", "none");
			context.Response.AddHeader("Content-Type", contentType);
			context.Response.ContentType = contentType;

			var outputStream = context.Response.OutputStream;

//			var acceptEncoding = context.Request.Headers["Accept-Encoding"].TrimToLower();
//			if(acceptEncoding != null && !contentType.StartsWith("image") && !contentType.StartsWith("sound") && !contentType.StartsWith("video"))
//			{
//				if(acceptEncoding.IndexOf("gzip", StringComparison.Ordinal) >= 0)
//				{
//					outputStream = new GZipStream(outputStream, CompressionMode.Compress, false);
//					context.Response.AddHeader("Content-Encoding", "gzip");
//				}
//				else if(acceptEncoding.IndexOf("deflate", StringComparison.Ordinal) >= 0)
//				{
//					outputStream = new DeflateStream(outputStream, CompressionMode.Compress, false);
//					context.Response.AddHeader("Content-Encoding", "deflate");
//				}
//			}

			using(outputStream)
			using(var stream = fileInfo.OpenRead())
			{
				context.Response.ContentLength64 = fileInfo.Length;
				stream.CopyTo(outputStream);
				outputStream.Flush();
			}
		}

		private FileInfo GetFileInfo(Uri requestUrl)
		{
			var requestPath = requestUrl.LocalPath;

			if(!requestPath.StartsWith(localPath))
				return null;

			var path = requestPath.Substring(localPath.Length);
			var fullpath = Path.GetFullPath(Path.Combine(root, path));

			//Don't hack me!
			if(!fullpath.StartsWith(root))
				return null;

			var fileInfo = new FileInfo(fullpath);
			if(fullpath == root || !fileInfo.Exists)
			{
				var filepath = DefaultFiles.Select(filename => Path.Combine(root, filename)).FirstOrDefault(File.Exists);
				if(filepath != null)
					fileInfo = new FileInfo(filepath);
			}
			return !fileInfo.Exists ? null : fileInfo;
		}

		private static string GetContentType(string fileExt)
		{
			return ContentTypes[fileExt] as string ?? "application/octet-stream";
		}

		private static readonly Hashtable ContentTypes = new Hashtable
		{
			{".txt", "text/plain"},
			{".htm", "text/html"},
			{".html", "text/html"},
			{".css", "text/css"},
			{".js", "application/javascript"},
			{".ico", "image/x-icon"},
			{".gif", "image/gif"},
			{".png", "image/png"},
			{".jpg", "image/jpeg"},
			{".jpeg", "image/jpeg"}
		};

		private static readonly string[] DefaultFiles =
		{
			"index.html",
			"default.html"
		};

		private const int MaxAge = 300;

		private readonly string root;
		private readonly string localPath;
	}
}