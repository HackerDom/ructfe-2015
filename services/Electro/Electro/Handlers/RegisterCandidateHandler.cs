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
	class RegisterCandidateHandler : AuthorizedBaseHandler
	{
		private readonly ElectroController electroController;

		public RegisterCandidateHandler(ElectroController electroController, AuthController authController, string prefix) : base(authController, prefix)
		{
			this.electroController = electroController;
		}

		protected override void ProcessAuthorizedRequest(HttpListenerContext context, User user)
		{
			context.Request.AssertMethod(WebRequestMethods.Http.Post);
			var form = context.Request.GetPostData();

			string electionIdString; Guid electionId;
			if(!form.TryGetValue("electionId", out electionIdString) || !Guid.TryParse(electionIdString, out electionId))
				throw new HttpException(HttpStatusCode.BadRequest, "Invalid request params");

			var success = electroController.RegisterCandidate(electionId, user);
			WriteData(context, success.ToJson());
		}
	}
}
