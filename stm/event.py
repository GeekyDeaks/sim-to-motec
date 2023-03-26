from datetime import datetime

class STMEvent:

    def __init__(self, 
                name = None,
                date = None,
                time = None,
                driver = None,
                vehicle = None,
                venue = None,
                shortcomment = None,
                session = None,
                comment = None ):
        
        now = datetime.now()

        if comment is None and  shortcomment is None:
            dt = now.strftime("%Y-%m-%d %H:%M:%S")
            shortcomment = f"converted by sim-to-motec at {dt}"

        if date is None and time is None:
            date = now.strftime('%d/%m/%Y')
            time = now.strftime('%H:%M:%S')

        self.name = name
        self.date = date
        self.time = time
        self.driver = driver
        self.vehicle = vehicle
        self.venue = venue
        self.shortcomment = shortcomment
        self.session = session
        self.comment = comment

