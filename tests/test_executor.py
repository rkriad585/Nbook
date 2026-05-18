import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.executor import run_python_stateful, get_variables, cancel_execution, PYTHON_GLOBALS


class TestExecutor:
    def setup_method(self):
        PYTHON_GLOBALS.clear()

    def test_simple_print(self):
        result = run_python_stateful('print("hello")')
        assert result['status'] == 'success'
        assert 'hello' in result['output']

    def test_eval_expression(self):
        result = run_python_stateful('2 + 2')
        assert result['status'] == 'success'
        assert '4' in result['output']

    def test_variable_persistence(self):
        run_python_stateful('x = 42')
        result = run_python_stateful('x')
        assert result['status'] == 'success'
        assert '42' in result['output']

    def test_syntax_error(self):
        result = run_python_stateful('print(')
        assert result['status'] == 'error'

    def test_runtime_error(self):
        result = run_python_stateful('1/0')
        assert result['status'] == 'error'
        assert 'division by zero' in result['output']

    def test_magic_command(self):
        result = run_python_stateful('!echo magic_test')
        assert result['status'] == 'success'
        assert 'magic_test' in result['output']

    def test_cancel_before_execution(self):
        cancel_execution()
        result = run_python_stateful('print("should not run")')
        assert result['status'] == 'cancelled'

    def test_get_variables(self):
        run_python_stateful('my_var = "test_value"')
        vars_result = get_variables()
        names = [v['name'] for v in vars_result]
        assert 'my_var' in names

    def test_get_variables_excludes_private(self):
        run_python_stateful('_private = 1')
        vars_result = get_variables()
        names = [v['name'] for v in vars_result]
        assert '_private' not in names

    def test_matplotlib_injection(self):
        result = run_python_stateful('import matplotlib; print("matplotlib imported")')
        assert result['status'] == 'success'

    def test_restart_clears_globals(self):
        run_python_stateful('x = 100')
        assert 'x' in [v['name'] for v in get_variables()]
        PYTHON_GLOBALS.clear()
        assert 'x' not in [v['name'] for v in get_variables()]
