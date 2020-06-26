# Stubs for prov.tests.test_dot (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional

from prov.tests.test_model import AllTestsBase
from prov.tests.utility import DocumentBaseTestCase

class SVGDotOutputTest(DocumentBaseTestCase, AllTestsBase):
    MIN_SVG_SIZE: int = ...
    def do_tests(self, prov_doc: Any, msg: Optional[Any] = ...) -> None: ...
