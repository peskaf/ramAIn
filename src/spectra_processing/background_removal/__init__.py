# njit decorator
def njit(*args, **kwargs):
    try:
        import numba

        return numba.njit(*args, **kwargs)

    except:
        warning_msg = "".join(
            [
                "Could not import numba. ",
                "Install numba to use JITed implementations of backend ",
                "functions for speed up of baseline removal algorithms",
            ]
        )

        from warnings import warn

        warn(warning_msg)

        def no_decorator(fn):
            return fn

        return no_decorator
