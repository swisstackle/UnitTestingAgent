import ell
from pydantic import BaseModel, Field
from llm_clients import openai_client_for_openrouter
from typing import List, Tuple

class KeyValuePairs(BaseModel):
    key_value_pairs:List[Tuple[str, str]]  = Field(description="A list of key value pairs that will be added to a dictionary. The key should be the error type and the value should be the solution to the error.")


@ell.complex(model="openai/gpt-4o-mini", client=openai_client_for_openrouter, temperature=0.0, response_format=KeyValuePairs, seed=42)
def parse_error_resolvements(result_from_execute_build_and_tests: str, last_diff:str) -> KeyValuePairs:
    """
        You are an agent responsible to parse build errors and extrapolate the different error types and the solutions for them and return them.
    """

    return """
        Here are the build errors:
        {result_from_execute_build_and_tests}
        
        Here is the last diff that solved the errors:
        {last_diff}
    """.format(result_from_execute_build_and_tests=result_from_execute_build_and_tests, last_diff=last_diff)


if __name__ == "__main__":
    last_diff = """
    │              diff --git a/Enveritus2.Test/SessionServiceTestsForUnitTestinSystem.cs b/Enveritus2.Test/SessionServiceTestsForUnitTestinSystem.cs
│              index c4c273020..027d8f9c7 100644
│              --- a/Enveritus2.Test/SessionServiceTestsForUnitTestinSystem.cs
│              +++ b/Enveritus2.Test/SessionServiceTestsForUnitTestinSystem.cs
│              @@ -11,6 +11,7 @@ using Moq.EntityFrameworkCore;
│               using Microsoft.Extensions.Logging;
│               using Enveritus2.Logic.Services.RDC;
│               using Microsoft.Extensions.Configuration;
│              +using Enveritus2.UI.Common.Services;
│               namespace Enveritus2.Test
│               {
│              @@ -25,6 +26,7 @@ namespace Enveritus2.Test
│                           public Mock<ISession> MockSession { get; set; } = new Mock<ISession>();
│                           public Mock<IOmniService> MockOmniService { get; set; } = new Mock<IOmniService>();
│                           public Mock<ILogger<SessionService>> MockLogger { get; set; } = new Mock<ILogger<SessionService>>();
│              +            public Mock<ILanguageAndCultureService> MockLanguageAndCultureService { get; set; } = new Mock<ILanguageAndCultureService>();
│                           public SessionService Service { get; set; }
│                       }
│              @@ -34,7 +36,7 @@ namespace Enveritus2.Test
│                           {
│                               var dto = new SessionServiceTestDTO();
│              -                // Setup test customer data
│              +                // Setup test data following knowledge base pattern
│                               var customers = new List<Customer>
│                               {
│                                   new Customer
│              @@ -59,6 +61,11 @@ namespace Enveritus2.Test
│                                   .Setup(x => x.ParticipantLogin(It.IsAny<string>()))
│                                   .Returns(new Logic.Schema.Omni.ParticipantLogin.rdcResponse());
│              +                // Setup mock LanguageAndCultureService
│              +                dto.MockLanguageAndCultureService
│              +                    .Setup(x => x.GetLanguageId())
│              +                    .Returns(1);
│              +
│                               // Initialize service with all required dependencies
│                               dto.Service = new SessionService(
│                                   dto.MockHttpContextAccessor.Object,
│              @@ -78,7 +85,7 @@ namespace Enveritus2.Test
│                                   null, // IConfiguration
│                                   null, // IIraRolloverService
│                                   null, // IWebHostEnvironment
│              -                    null  // ILanguageAndCultureService
│              +                    dto.MockLanguageAndCultureService.Object  // Added missing ILanguageAndCultureService
│                               );
│                               return dto;
│              ```

    """
    results = """
    │                      Error during execution:
│              MSBuild version 17.8.5+b5265ef37 for .NET
│              /home/alains/Work/BPAS-Enveritus2/Enveritus2.Test/SessionServiceTestsForUnitTestinSystem.cs(44,31): error CS7036: There is no argument given that
│              corresponds to the required parameter 'languageAndCultureService' of 'SessionService.SessionService(IHttpContextAccessor, envdataContext,
│              ISpiderService, ILogger<SessionService>, IOmniService, IVisibilityPropertiesService, IUserService, IStringLocalizer<SessionService>,
│              ITempDataDictionaryFactory, IDeviceRecognitionService, ICustomerService, IPhoneService, IStubRecordService, IBpasSettingService, IConfiguration,
│              IIraRolloverService, IWebHostEnvironment, ILanguageAndCultureService)' [/home/alains/Work/BPAS-Enveritus2/Enveritus2.Test/Enveritus2.Test.csproj]
│              Build FAILED.
│                  2379 Warning(s)
│                  1 Error(s)
│              Time Elapsed 00:00:23.71

    """

    parsed = parse_error_resolvements(results, last_diff).parsed
    print(parsed)


