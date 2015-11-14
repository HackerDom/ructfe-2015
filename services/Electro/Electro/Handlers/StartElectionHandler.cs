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
	class StartElectionHandler : AuthorizedBaseHandler
	{
		private readonly ElectroController electroController;

		public StartElectionHandler(ElectroController electroController, AuthController authController, string prefix) : base(authController, prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessAuthorizedRequest(HttpListenerContext context, User user)
		{
			context.Request.AssertMethod(WebRequestMethods.Http.Post);
			var form = context.Request.GetPostData();
			string electionName;
			string isPublicString; bool isPublic;
			string tillString; DateTime till;
			if(!form.TryGetValue("name", out electionName) ||
			   !form.TryGetValue("isPublic", out isPublicString) || !bool.TryParse(isPublicString, out isPublic) ||
			   !form.TryGetValue("till", out tillString) || !DateTime.TryParse(tillString, out till) || till < DateTime.UtcNow)
			{
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");
			}

			var election = electroController.StartElection(electionName, user, isPublic, till);
			WriteData(context, election.ToJson(useSimpleDictionaryFormat:true));
		}
	}
}
