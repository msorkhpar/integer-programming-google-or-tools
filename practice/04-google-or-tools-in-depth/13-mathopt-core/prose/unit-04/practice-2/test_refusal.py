from ortools.math_opt.python import mathopt

from refusal import refusal

S = mathopt.SolverType


def depots() -> mathopt.Model:
    """Open warehouses (yes/no) for a logistics platform's region."""
    model = mathopt.Model(name="depots")
    a, b = model.add_binary_variable(name="open_a"), model.add_binary_variable(name="open_b")
    model.add_linear_constraint(a + b >= 1, name="serve")
    model.minimize(4 * a + 3 * b)
    return model


def raised(call) -> BaseException:
    try:
        call()
    except Exception as error:
        return error
    raise AssertionError("the call was not refused")


def test_a_refused_parameter_gives_its_code_and_message():
    error = raised(lambda: mathopt.solve(depots(), S.HIGHS, params=mathopt.SolveParameters(threads=3)))
    assert refusal(error) == ("INVALID_ARGUMENT", "threads not supported for HiGHS solver, this must be set "
                                                  "using globals, see HiGHS documentation")


def test_a_refused_model_gives_its_code_and_message():
    error = raised(lambda: mathopt.solve(depots(), S.GLOP))
    assert refusal(error) == ("INVALID_ARGUMENT", "Glop does not support integer variables")


def test_an_unimplemented_feature_gives_its_own_code():
    model = depots()
    a = model.add_variable(lb=0, ub=2, name="spare")
    model.minimize(a * a)
    code, message = refusal(raised(lambda: mathopt.solve(model, S.HIGHS)))
    assert code == "UNIMPLEMENTED"
    assert "quadratic objectives" in message


def test_an_exception_mathopt_converted_is_read_from_its_suffix():
    error = ValueError("node_limit not supported for CP-SAT (was C++ INVALID_ARGUMENT)")
    assert refusal(error) == ("INVALID_ARGUMENT", "node_limit not supported for CP-SAT")


def test_an_error_with_no_status_is_unknown():
    assert refusal(RuntimeError("bad_function_call")) == ("UNKNOWN", "bad_function_call")
    assert refusal(AttributeError("'NoneType' object has no attribute 'x'")) == (
        "UNKNOWN", "'NoneType' object has no attribute 'x'")
