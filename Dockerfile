FROM python:3
RUN python -m pip install pulp
ADD . .
CMD ["python", "WhiskasModel1.py"]