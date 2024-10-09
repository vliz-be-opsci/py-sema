# your_submodule/tests/test_example.py

from .base import TestBase, TestResult


class ExampleTest(TestBase):
    def run(self) -> TestResult:
        try:
            # Example test logic
            print(
                f"Running example test on {self.url} with options {self.options}"
            )
            # Simulate success
            self.result.url = self.url
            self.result.type = self.type
            self.result.success = True
            self.result.message = "Example test passed."
        except Exception as e:
            self.result.error = True
            self.result.message = str(e)
        return self.result


# More tests can be added here
# TODO: Add sema-get tests :
# 1. Test for successful response
# 2. check for syntax errors in response
# 3. Test for min-ammount of triples in response
# 4. Test for specific triples in response with shacl validation

# TODO: Add sema-conneg tests :
# 1. Test for successful response
# 2. check for all available MIME types in response and compare with expected
# 3. check content disposition header for filename
# 4. check contents for specific triples with shacl validation

# TODO: Add sema-ldes tests :
# 1. Test for successful response
# 2. check if url can traverse to the next X pages
# 3. check caching headers
# 4. check for specific triples with shacl validation if LDES shape complies to
#    spec and if contents are valid and compliant to shape provided
