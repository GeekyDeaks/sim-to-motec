from datetime import datetime as dt

class STMEvent:

    def __init__(self, 
                name = "",
                datetime = None,
                driver = "",
                vehicle = "",
                venue = "",
                shortcomment = "",
                session = "",
                comment = "" ):
        
        now = dt.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        if datetime is None:
            datetime = now

        if not comment and not shortcomment:
            shortcomment = f"converted by sim-to-motec at {now}"

        self.datetime = datetime
        self.name = name
        self.driver = driver
        self.vehicle = vehicle
        self.venue = venue
        self.shortcomment = shortcomment
        self.session = session
        self.comment = comment

