import subprocess
import unittest


class Test_BWA_Example(unittest.TestCase):
    def test_something(self) -> None:
        code: int = subprocess.call(["/bin/bash", "run_module_d"])
        self.assertTrue(code == 0)
        assert code == 0


if __name__ == "__main__":
    unittest.main()
