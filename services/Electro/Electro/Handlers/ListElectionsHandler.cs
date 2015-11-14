using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	class ListElectionsHandler : BaseHttpHandler
	{
		private readonly ElectroController electroController;

		public ListElectionsHandler(ElectroController electroController, string prefix) : base(prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessRequest(HttpListenerContext context)
		{
			var finishedString = context.Request.QueryString["finished"];
			bool finished;
			if(!bool.TryParse(finishedString, out finished))
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");

			ElectionPulicCore[] elections;
			if(finished)
				elections = electroController.GetFinishedElections().Select(ElectionPulicCore.Create).ToArray();
			else
				elections = electroController.GetUnfinishedPublicElections().Select(ElectionPulicCore.Create).ToArray();

			WriteData(context, elections.ToJson());
		}
	}
}
