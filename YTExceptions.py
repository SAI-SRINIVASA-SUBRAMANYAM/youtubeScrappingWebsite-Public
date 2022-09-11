class YTExceptions:
    def __init__(self, message: str, src: str, severity: str = "H"):
        """
        :param message: Description of the error
        :param src: Source of the error being raised
        :param severity: "H": "high", "M": "medium", "L": "low"
        """
        raise Exception({"message": message, "src": src, "severity": severity})
