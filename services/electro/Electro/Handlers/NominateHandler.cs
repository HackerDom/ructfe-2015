using System;
using System.Net;
using Electro.Model;
using Electro.Utils;

namespace Electro.Handlers
{
	class NominateHandler : AuthorizedBaseHandler
	{
		private readonly ElectroController electroController;

		public NominateHandler(ElectroController electroController, AuthController authController, string prefix) : base(authController, prefix)
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

			var privateKey = electroController.NominateCandidate(electionId, user);
			if(privateKey == null)
				throw new HttpException(HttpStatusCode.BadRequest, "Nominate FAILED");

			WriteData(context, privateKey.ToJson());
		}
	}
}
