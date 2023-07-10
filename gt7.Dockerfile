FROM python:3.9

ENV PLAYSTATION_IP=$PLAYSTATION_IP
ENV DRIVER_NAME=$DRIVER_NAME

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt


ADD https://raw.githubusercontent.com/ddm999/gt7info/web-new/_data/db/cars.csv stm/gt7/db/cars.csv
ADD https://raw.githubusercontent.com/ddm999/gt7info/web-new/_data/db/course.csv stm/gt7/db/course.csv

RUN chmod -R 755 stm/gt7/db/

CMD [ "python", "gt7-cli.py", "--driver", "$DRIVER_NAME", "$PLAYSTATION_IP"]
