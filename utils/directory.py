import os

directory = os.path.join(
    *(os.path.split(
        os.path.dirname(
            os.path.abspath(
                __file__
            )
        )
    ))[:-1]
)
