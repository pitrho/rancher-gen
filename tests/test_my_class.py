from mock import patch
from rho_boilerplate_package.my_tool import MyClass


class TestMyTool:

    def setup_method(self, method):
        self.my_class = MyClass()

    def test_start_command(self):
        result = self.my_class.start()
        assert result == 'Foo Bar'
