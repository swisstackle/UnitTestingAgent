import re
from project_names_utils import get_project_references, find_unreferenced_csproj_files
from project_file_agents import add_project_references

def strip_comments(code):
    """
    Strips C# comments from code while preserving line numbers.
    Handles both single-line and multi-line comments.
    """
    # Replace multi-line comments with empty lines to preserve line numbers
    code = re.sub(r'/\*[\s\S]*?\*/', lambda m: '\n' * m.group().count('\n'), code)
    
    # Replace single-line comments with empty lines
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    
    return code

def update_project_file(test_file_content, test_file_path, root_directory, project_file_path):
    # Strip comments while preserving line numbers
    cleaned_content = strip_comments(test_file_content)
    
    # Extracting namespace and class names from the cleaned content
    namespace_match = re.search(r'namespace\s+([a-zA-Z0-9_\.]+)(?:\s)*{', cleaned_content, re.MULTILINE)
    
    # Updated class pattern to be more specific to C# class declarations
    class_matches = re.finditer(
        r'(?:public|private|internal|protected)?\s+(?:static|sealed|abstract)?\s*class\s+(\w+)(?:\s*:|\s*{|\s+where\b)',
        cleaned_content
    )
    
    # Find the test class (not DTO or Factory)
    test_class_name = None
    for match in class_matches:
        class_name = match.group(1)
        if not any(suffix in class_name for suffix in ['DTO', 'Factory']):
            test_class_name = class_name
            break
    
    namespace_name = namespace_match.group(1) if namespace_match else None
    namespace_and_classname = f"{namespace_name}.{test_class_name}" if namespace_name and test_class_name else test_class_name
    
    # Rest of the function remains the same
    project_references = get_project_references(test_file_path, root_directory)
    unreferenced_csproj_files = find_unreferenced_csproj_files(project_file_path, project_references)
    function_calls = add_project_references(project_file_path, unreferenced_csproj_files)
    for tool_call in function_calls.tool_calls:
        tool_call()
    return namespace_and_classname

def main():
    # Test file content (the C# code you provided)
    test_file_content = '''
// Required using statements per knowledge base
using Xunit;
using Moq;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Enveritus2.Services;
using Enveritus2.Envdata.DAL.Entities;
using Enveritus2.Logic.Services;
using Enveritus2.Logic.Services.DataRefresh;
using Enveritus2.Logic.Services.RDC;
using Enveritus2.Logic.Services.Settings;
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.EntityFrameworkCore;
using Enveritus2.UI.Common.Services;
using Microsoft.AspNetCore.Mvc.ViewFeatures;
using Microsoft.Extensions.Configuration;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Localization;
using Moq.EntityFrameworkCore;

namespace Enveritus2.Test // Required namespace per specifications
{
    public class SessionServiceTests
    {
        // DTO class to encapsulate test dependencies per knowledge base
        public class SessionServiceTestDTO
        {
            public Mock<envdataContext> MockDb { get; set; } = new Mock<envdataContext>();
            public Mock<IHttpContextAccessor> MockContextAccessor { get; set; } = new Mock<IHttpContextAccessor>();
            public Mock<IStubRecordService> MockStubRecordService { get; set; } = new Mock<IStubRecordService>();
            public Mock<IOmniService> MockOmniService { get; set; } = new Mock<IOmniService>();
            public Mock<ILogger<SessionService>> MockLogger { get; set; } = new Mock<ILogger<SessionService>>();
            public Mock<ILanguageAndCultureService> MockLanguageAndCultureService { get; set; } = new Mock<ILanguageAndCultureService>();
            public Mock<ITempDataDictionaryFactory> MockTempDataFactory { get; set; } = new Mock<ITempDataDictionaryFactory>();
            public Mock<ISession> MockSession { get; set; } = new Mock<ISession>();
            public Mock<HttpContext> MockHttpContext { get; set; } = new Mock<HttpContext>();
            public SessionService Service { get; set; }
        }

        // Factory class for creating test dependencies per knowledge base
        public static class SessionServiceTestFactory 
        {
            public static SessionServiceTestDTO Create()
            {
                var dto = new SessionServiceTestDTO();

                // Setup test data per knowledge base
                var customers = new List<Customer>
                {
                    new Customer
                    {
                        CustomerId = "1",
                        LoginId = "testLogin", 
                        UserName = "testUser"
                    }
                };  
                dto.MockDb.Setup(x => x.Customer).ReturnsDbSet(customers);

                // Setup session per knowledge base example
                dto.MockSession.Setup(s => s.Set(It.IsAny<string>(), It.IsAny<byte[]>()));
                dto.MockSession.Setup(s => s.TryGetValue(It.IsAny<string>(), out It.Ref<byte[]>.IsAny))
                    .Returns(true);

                dto.MockHttpContext.Setup(c => c.Session).Returns(dto.MockSession.Object);
                dto.MockContextAccessor.Setup(x => x.HttpContext).Returns(dto.MockHttpContext.Object);

                var tempData = new Mock<ITempDataDictionary>();
                dto.MockTempDataFactory.Setup(x => x.GetTempData(It.IsAny<HttpContext>()))
                    .Returns(tempData.Object);

                // Create service with all required dependencies using proper Moq syntax
                dto.Service = new SessionService(
                    dto.MockContextAccessor.Object,
                    dto.MockDb.Object, 
                    new Mock<ISpiderService>().Object,
                    dto.MockLogger.Object,
                    dto.MockOmniService.Object,
                    new Mock<IVisibilityPropertiesService>().Object,
                    new Mock<IUserService>().Object,
                    new Mock<IStringLocalizer<SessionService>>().Object,
                    dto.MockTempDataFactory.Object,
                    new Mock<IDeviceRecognitionService>().Object,
                    new Mock<ICustomerService>().Object,
                    new Mock<IPhoneService>().Object,
                    dto.MockStubRecordService.Object,
                    new Mock<IBpasSettingService>().Object,
                    new Mock<IConfiguration>().Object,
                    new Mock<IIraRolloverService>().Object,
                    new Mock<IWebHostEnvironment>().Object,
                    dto.MockLanguageAndCultureService.Object
                );

                return dto;
            }
        }

        [Fact] // Test valid login ID scenario per knowledge base
        public void ConfigureSessionForParticipantByLoginId_ValidLoginId_ConfiguresSession()
        {
            var dto = SessionServiceTestFactory.Create();
            
            dto.Service.ConfigureSessionForParticipantByLoginId("testLogin", null);

            dto.MockStubRecordService.Verify(
                x => x.GenerateAllStubRecordsForParticipant(
                    It.IsAny<string>(),
                    It.IsAny<Logic.Schema.Omni.ParticipantLogin.rdcResponse>()),
                Times.Once);
        }

        [Fact] // Test null login ID scenario per knowledge base
        public void ConfigureSessionForParticipantByLoginId_NullLoginId_ThrowsException()
        {
            var dto = SessionServiceTestFactory.Create();
            
            Assert.Throws<Exception>(() => dto.Service.ConfigureSessionForParticipantByLoginId(null, null));
        }

        [Fact] // Test nonexistent login ID scenario per knowledge base
        public void ConfigureSessionForParticipantByLoginId_NonExistentLoginId_ThrowsException()
        {
            var dto = SessionServiceTestFactory.Create();
            
            Assert.Throws<Exception>(() => dto.Service.ConfigureSessionForParticipantByLoginId("nonexistent", null));
        }

        [Fact] // Test with plan ID scenario per knowledge base
        public void ConfigureSessionForParticipantByLoginId_WithPlanId_GeneratesStubRecords()
        {
            var dto = SessionServiceTestFactory.Create();
            const string planId = "testPlan";
            
            dto.Service.ConfigureSessionForParticipantByLoginId("testLogin", planId);

            dto.MockStubRecordService.Verify(
                x => x.GenerateStubRecords(It.IsAny<string>(), planId),
                Times.Once);
        }

        [Fact] // Test empty login ID scenario per knowledge base
        public void ConfigureSessionForParticipantByLoginId_EmptyLoginId_ThrowsException()
        {
            var dto = SessionServiceTestFactory.Create();
            
            Assert.Throws<Exception>(() => dto.Service.ConfigureSessionForParticipantByLoginId("", null));
        }

        [Fact] // Test database error scenario per knowledge base
        public void ConfigureSessionForParticipantByLoginId_DatabaseError_LogsAndThrowsException()
        {
            var dto = SessionServiceTestFactory.Create();
            dto.MockDb.Setup(x => x.Customer).Throws(new Exception("Database error"));

            var ex = Assert.Throws<Exception>(() => dto.Service.ConfigureSessionForParticipantByLoginId("testLogin", null));

            dto.MockLogger.Verify(
                x => x.Log(
                    LogLevel.Error,
                    It.IsAny<EventId>(),
                    It.Is<It.IsAnyType>((v, t) => true),
                    It.IsAny<Exception>(),
                    It.IsAny<Func<It.IsAnyType, Exception, string>>()),
                Times.AtLeastOnce);
        }
    }
}

'''  # Your complete test file content here
    
    # Test parameters
    test_file_path = "path/to/SessionServiceTests.cs"
    root_directory = "path/to/root"
    project_file_path = "path/to/project.csproj"
    
    # Run the function
    try:
        result = update_project_file(test_file_content, test_file_path, root_directory, project_file_path)
        print("\nTest Results:")
        print("-" * 50)
        print(f"Extracted namespace and class name: {result}")
        
        # Additional verification
        expected_result = "Enveritus2.Test.SessionServiceTests"
        if result == expected_result:
            print("\nSUCCESS: Correctly extracted namespace and class name!")
        else:
            print(f"\nFAILURE: Expected '{expected_result}' but got '{result}'")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    main()
