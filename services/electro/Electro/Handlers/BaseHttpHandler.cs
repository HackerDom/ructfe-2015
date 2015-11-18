using System;
using System.Diagnostics;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Electro.Utils;
using log4net;

namespace Electro.Handlers
{
	public abstract class BaseHttpHandler
	{
		protected BaseHttpHandler(string prefix)
		{
			listener = new HttpListener();
			this.prefix = prefix;
			listener.Prefixes.Add(this.prefix);
		}

		public void Start()
		{
			log.InfoFormat("Starting to listen '{0}'", prefix);
			listener.Start();
			listener.BeginGetContext(Callback, null);
		}

		private void Callback(IAsyncResult result)
		{
			listener.BeginGetContext(Callback, null);
			var context = listener.EndGetContext(result);
			Task.Run(() =>
			{
				if(Thread.CurrentThread.IsThreadPoolThread)
					Thread.CurrentThread.Name = Thread.CurrentThread.ManagedThreadId.ToString();

				var sw = Stopwatch.StartNew();
				int hash = 0;
				try
				{
					hash = Math.Abs(new object().GetHashCode());
					context.Response.KeepAlive = true;

					if(!(this is StaticHandler))
						log.InfoFormat("Start processing #{0} {1} {2} {3}", hash, context.Request.RemoteEndPoint, context.Request.HttpMethod, context.Request.Url);
					ProcessRequest(context);
				}
				catch(HttpException exception)
				{
					log.Error(exception);
					Error(context, exception.Status, exception.Message);
				}
				catch(Exception exception)
				{
					log.Error(exception);
					Error(context, HttpStatusCode.InternalServerError, "Internal server error");
				}
				finally
				{
					if(!(this is StaticHandler))
						log.InfoFormat("Finished processing #{0} in {1}ms {2} {3}", hash, sw.ElapsedMilliseconds, context.Request.HttpMethod, context.Request.RawUrl);
				}
				CommonUtils.Try(() => context.Response.Close());
			});
		}

		protected static void WriteString(HttpListenerContext context, string msg)
		{
			context.Response.ContentType = "text/plain; charset=utf-8";
			Write(context, msg == null ? null : Encoding.UTF8.GetBytes(msg));
		}

		protected static void WriteData(HttpListenerContext context, byte[] data, string contentType = "application/json; charset=utf-8")
		{
			context.Response.ContentType = contentType;
			Write(context, data ?? EmptyJson);
		}

		private static void Write(HttpListenerContext context, byte[] data)
		{
			var response = context.Response;
			if(data == null)
			{
				response.ContentLength64 = 0;
				return;
			}
			response.ContentLength64 = data.Length;
			response.OutputStream.Write(data, 0, data.Length);
		}

		protected abstract void ProcessRequest(HttpListenerContext context);

		private static void Error(HttpListenerContext context, HttpStatusCode status, string msg)
		{
			CommonUtils.Try(() =>
			{
				log.InfoFormat("{0} - {1}: {2}", status, status, msg);
				var response = context.Response;
				response.Headers.Clear();
				response.StatusCode = (int)status;
				response.ContentType = "text/plain; charset=utf-8";
				if(string.IsNullOrEmpty(msg))
				{
					response.ContentLength64 = 0;
					return;
				}
				var bytes = Encoding.UTF8.GetBytes(msg);
				response.ContentLength64 = bytes.Length;
				response.OutputStream.Write(bytes, 0, bytes.Length);
			});
		}

		private readonly string prefix;

		private static readonly byte[] EmptyJson = Encoding.UTF8.GetBytes("{}");
		private static readonly ILog log = LogManager.GetLogger(typeof(BaseHttpHandler));
		private readonly HttpListener listener;
	}
}