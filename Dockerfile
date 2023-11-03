FROM python:3
RUN python -m pip install pulp pandas
ADD . .
CMD ["python", "WhiskasModel1.py"]