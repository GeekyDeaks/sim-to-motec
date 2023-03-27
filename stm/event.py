from datetime import datetime

class STMEvent:

    def __init__(self, 
                name = "",
                date = "",
                time = "",
                driver = "",
                vehicle = "",
                venue = "",
                shortcomment = "",
                session = "",
                comment = "" ):
        
        now = datetime.now()

        if not comment and not shortcomment:
            dt = now.strftime("%Y-%m-%d %H:%M:%S")
            shortcomment = f"converted by sim-to-motec at {dt}"

        if not date and not time:
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

